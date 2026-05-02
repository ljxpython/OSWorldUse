from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from osworld_cua_bridge.launcher import DEFAULT_CUA_CONFIG_PATH, resolve_cua_command
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
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
