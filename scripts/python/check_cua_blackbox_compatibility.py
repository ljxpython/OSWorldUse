from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import subprocess
import sys
import threading
import time
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from osworld_cua_bridge.launcher import DEFAULT_CUA_CONFIG_PATH, resolve_cua_command, target_os_from_os_type
from osworld_cua_bridge.protocol import BRIDGE_PROTOCOL_VERSION
from scripts.python.cua_blackbox_defaults import CUA_BLACKBOX_CASES_DIR
from scripts.python.validate_cua_regression_cases import DEFAULT_CASES_DIR, DEFAULT_META_PATH, validate_cases


REQUIRED_RUN_FLAGS = (
    "--config",
    "--runs-dir",
    "--openclaw-bin",
    "--target-os",
    "--target-screen",
    "--target-dpr",
    "--max-steps",
    "--max-duration-ms",
    "--max-step-duration-ms",
)


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check CUA blackbox compatibility inputs without running a benchmark")
    parser.add_argument("--cua_bin", type=str, default=_env_str("OSWORLD_CUA_BIN"))
    parser.add_argument("--cua_config_path", type=str, default=_env_str("OSWORLD_CUA_CONFIG_PATH", DEFAULT_CUA_CONFIG_PATH))
    parser.add_argument("--cua_version", type=str, default=_env_str("OSWORLD_CUA_VERSION"))
    parser.add_argument("--meta_path", type=str, default=DEFAULT_META_PATH)
    parser.add_argument("--cases_dir", type=str, default=DEFAULT_CASES_DIR)
    parser.add_argument("--cua_cases_dir", type=str, default=CUA_BLACKBOX_CASES_DIR)
    parser.add_argument("--openclaw_bin", type=str, default=_env_str("OSWORLD_OPENCLAW_BIN", os.path.join(ROOT_DIR, "osworld_cua_bridge", "bin", "openclaw")))
    parser.add_argument("--result_dir", type=str, default="./results_cua_compatibility")
    parser.add_argument("--timeout_seconds", type=float, default=20)
    parser.add_argument("--skip_cli", action="store_true", help="Skip cua --help checks and only validate files/cases")
    return parser.parse_args()


def _env_str(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def _sha256(path: str | None) -> str | None:
    if not path:
        return None
    expanded = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
    if not os.path.isfile(expanded):
        return None
    digest = hashlib.sha256()
    with open(expanded, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _abs_path(path: str | None) -> str:
    if not path:
        return ""
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def _command_binary_path(command: list[str]) -> str | None:
    if not command:
        return None
    candidate = command[1] if len(command) >= 2 and os.path.basename(command[0]) == "node" else command[0]
    expanded = os.path.abspath(os.path.expanduser(os.path.expandvars(candidate)))
    return expanded if os.path.isfile(expanded) else None


def _run_help(command: list[str], args: list[str], timeout_seconds: float) -> dict[str, Any]:
    full_command = [*command, *args]
    started_at = time.time()
    try:
        completed = subprocess.run(
            full_command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "command": full_command,
            "exit_code": int(completed.returncode),
            "duration_seconds": time.time() - started_at,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except Exception as exc:
        return {
            "command": full_command,
            "exit_code": None,
            "duration_seconds": time.time() - started_at,
            "stdout": "",
            "stderr": str(exc),
        }


def _check(name: str, passed: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details or {}}


def _help_text(result: dict[str, Any]) -> str:
    return f"{result.get('stdout') or ''}\n{result.get('stderr') or ''}"


class _InvokeHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/invoke":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length") or "0")
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"_invalid": body}
        self.server.received_payloads.append(payload)  # type: ignore[attr-defined]

        response = json.dumps({"ok": True, "payload": {"type": "tool_result", "output": "ok"}}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: Any) -> None:
        return


def _run_openclaw_invoke(
    openclaw_bin: str,
    bridge_url: str,
    command: str,
    params: dict[str, Any],
    *,
    node_id: str,
    run_id: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    env = os.environ.copy()
    env.update(
        {
            "OSWORLD_CUA_BRIDGE_URL": bridge_url,
            "OSWORLD_CUA_NODE_ID": node_id,
            "OSWORLD_CUA_RUN_ID": run_id,
        }
    )
    full_command = [
        sys.executable,
        openclaw_bin,
        "nodes",
        "invoke",
        "--node",
        node_id,
        "--command",
        command,
        "--params",
        json.dumps(params, ensure_ascii=False),
    ]
    started_at = time.time()
    try:
        completed = subprocess.run(
            full_command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
            env=env,
        )
        parsed_stdout: dict[str, Any] | None = None
        try:
            parsed_stdout = json.loads(completed.stdout)
        except json.JSONDecodeError:
            parsed_stdout = None
        return {
            "command": command,
            "exit_code": int(completed.returncode),
            "duration_seconds": time.time() - started_at,
            "stdout": completed.stdout[-1000:],
            "stderr": completed.stderr[-1000:],
            "parsed_stdout": parsed_stdout,
        }
    except Exception as exc:
        return {
            "command": command,
            "exit_code": None,
            "duration_seconds": time.time() - started_at,
            "stdout": "",
            "stderr": str(exc),
            "parsed_stdout": None,
        }


def _check_openclaw_command_contract(openclaw_bin: str, timeout_seconds: float) -> dict[str, Any]:
    if not os.path.isfile(openclaw_bin):
        return {"passed": False, "reason": "openclaw shim not found", "results": []}

    server = ThreadingHTTPServer(("127.0.0.1", 0), _InvokeHandler)
    server.received_payloads = []  # type: ignore[attr-defined]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    bridge_url = f"http://127.0.0.1:{server.server_address[1]}"
    node_id = "compat-node"
    run_id = "compat-run"
    results: list[dict[str, Any]] = []
    failures: list[str] = []
    try:
        cases = [
            ("legacy_cua_run", "cua.run", {"runId": run_id, "reqId": "legacy", "tool": "get_screen_size", "args": {}}, True, "get_screen_size"),
            ("alias_run", "run", {"runId": run_id, "reqId": "alias", "tool": "get_cursor_position", "args": {}}, True, "get_cursor_position"),
            ("new_cua_tool", "cua.screenshot", {"runId": "native-run", "reqId": "new-tool", "args": {}}, True, "screenshot"),
            ("mismatch", "cua.screenshot", {"runId": run_id, "reqId": "mismatch", "tool": "mouse_click", "args": {}}, False, None),
        ]
        for case_name, command, params, should_pass, expected_tool in cases:
            before_count = len(server.received_payloads)  # type: ignore[attr-defined]
            result = _run_openclaw_invoke(
                openclaw_bin,
                bridge_url,
                command,
                params,
                node_id=node_id,
                run_id=run_id,
                timeout_seconds=timeout_seconds,
            )
            received = list(server.received_payloads)  # type: ignore[attr-defined]
            new_payload = received[-1] if len(received) > before_count else None
            result["case"] = case_name
            result["received_payload"] = new_payload
            results.append(result)

            parsed = result.get("parsed_stdout") or {}
            if should_pass:
                if result.get("exit_code") != 0 or parsed.get("ok") is not True:
                    failures.append(f"{case_name} did not return ok")
                    continue
                if not isinstance(new_payload, dict):
                    failures.append(f"{case_name} did not reach bridge")
                    continue
                if new_payload.get("tool") != expected_tool:
                    failures.append(f"{case_name} tool mismatch: {new_payload.get('tool')} != {expected_tool}")
                if new_payload.get("runId") != run_id:
                    failures.append(f"{case_name} runId was not normalized")
                if case_name == "new_cua_tool" and new_payload.get("cuaRunId") != "native-run":
                    failures.append("new_cua_tool did not preserve original CUA runId")
            else:
                if result.get("exit_code") == 0 or parsed.get("ok") is not False:
                    failures.append(f"{case_name} should fail with a structured error")
                if len(received) != before_count:
                    failures.append(f"{case_name} should not reach bridge")
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()

    return {"passed": not failures, "failures": failures, "results": results}


def _check_target_os_mapping() -> dict[str, Any]:
    expected = {
        "Windows": "win32",
        "win32": "win32",
        "Ubuntu": "linux",
        "Darwin": "darwin",
        "macOS": "darwin",
        "mac": "darwin",
    }
    actual = {os_type: target_os_from_os_type(os_type) for os_type in expected}
    failures = [f"{os_type}: {actual[os_type]} != {target}" for os_type, target in expected.items() if actual[os_type] != target]
    return {"passed": not failures, "expected": expected, "actual": actual, "failures": failures}


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    result_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.result_dir)))
    config_path = _abs_path(args.cua_config_path)
    meta_path = os.path.abspath(os.path.expanduser(os.path.expandvars(args.meta_path)))
    cases_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.cases_dir)))
    cua_cases_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.cua_cases_dir)))
    openclaw_bin = _abs_path(args.openclaw_bin)
    cua_command = resolve_cua_command(args.cua_bin)
    cua_binary_path = _command_binary_path(cua_command)

    checks: list[dict[str, Any]] = []
    checks.append(_check("cua_config_exists", os.path.isfile(config_path), {"path": config_path}))
    checks.append(_check("openclaw_exists", os.path.isfile(openclaw_bin), {"path": openclaw_bin}))
    checks.append(_check("cua_binary_resolved", bool(cua_binary_path), {"command": cua_command, "binary_path": cua_binary_path}))
    target_os_mapping = _check_target_os_mapping()
    checks.append(_check("target_os_mapping", target_os_mapping["passed"], target_os_mapping))
    openclaw_contract = _check_openclaw_command_contract(openclaw_bin, args.timeout_seconds)
    checks.append(_check("openclaw_shim_command_contract", openclaw_contract["passed"], openclaw_contract))

    rows, case_errors = validate_cases(meta_path, cases_dir, cua_cases_dir)
    checks.append(
        _check(
            "regression_cases_static",
            not case_errors,
            {"meta_path": meta_path, "cases_dir": cases_dir, "cua_cases_dir": cua_cases_dir, "task_count": len(rows), "errors": case_errors},
        )
    )

    cli_results: dict[str, Any] = {}
    if args.skip_cli:
        checks.append(_check("cua_cli_help", True, {"skipped": True}))
        checks.append(_check("cua_run_help_contract", True, {"skipped": True}))
    else:
        cua_help = _run_help(cua_command, ["--help"], args.timeout_seconds)
        run_help = _run_help(cua_command, ["run", "--help"], args.timeout_seconds)
        cli_results = {"cua_help": cua_help, "run_help": run_help}

        checks.append(_check("cua_cli_help", cua_help.get("exit_code") == 0, {"exit_code": cua_help.get("exit_code")}))

        run_text = _help_text(run_help)
        missing_flags = [flag for flag in REQUIRED_RUN_FLAGS if flag not in run_text]
        has_node_flag = "--nodeid" in run_text or "--node-id" in run_text
        if not has_node_flag:
            missing_flags.append("--nodeid|--node-id")
        checks.append(
            _check(
                "cua_run_help_contract",
                run_help.get("exit_code") == 0 and not missing_flags,
                {"exit_code": run_help.get("exit_code"), "missing_flags": missing_flags},
            )
        )

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "result_dir": result_dir,
        "bridge_protocol_version": BRIDGE_PROTOCOL_VERSION,
        "cua_version": args.cua_version,
        "cua_command": cua_command,
        "cua_binary_path": cua_binary_path,
        "cua_binary_sha256": _sha256(cua_binary_path),
        "cua_config_path": config_path,
        "cua_config_sha256": _sha256(config_path),
        "openclaw_bin": openclaw_bin,
        "openclaw_sha256": _sha256(openclaw_bin),
        "meta_path": meta_path,
        "meta_sha256": _sha256(meta_path),
        "cases_dir": cases_dir,
        "cua_cases_dir": cua_cases_dir,
        "checks": checks,
        "cli_results": cli_results,
        "passed": all(check["passed"] for check in checks),
    }
    return report


def main() -> int:
    args = config()
    report = build_report(args)
    result_dir = report["result_dir"]
    os.makedirs(result_dir, exist_ok=True)
    report_path = os.path.join(result_dir, "compatibility_report.json")
    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"compatibility_report: {report_path}")
    for check in report["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"{status} {check['name']}")
        details = check.get("details") or {}
        if details.get("missing_flags"):
            print(f"  missing_flags: {', '.join(details['missing_flags'])}")
        if details.get("errors"):
            for error in details["errors"]:
                print(f"  {error}")
        if details.get("failures"):
            for failure in details["failures"]:
                print(f"  {failure}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
