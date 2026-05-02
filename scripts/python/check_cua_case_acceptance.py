from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from scripts.python.validate_cua_regression_cases import DEFAULT_CASES_DIR, DEFAULT_META_PATH, validate_cases
from scripts.python.cua_blackbox_defaults import CUA_BLACKBOX_CASES_DIR
from scripts.python.cua_case_resolver import resolve_case_path


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run staged acceptance checks for new CUA blackbox evaluation cases")
    parser.add_argument("--meta_path", type=str, default=DEFAULT_META_PATH)
    parser.add_argument("--cases_dir", type=str, default=DEFAULT_CASES_DIR)
    parser.add_argument("--cua_cases_dir", type=str, default=CUA_BLACKBOX_CASES_DIR)
    parser.add_argument("--result_dir", type=str, default="./results_cua_case_acceptance")
    parser.add_argument("--domain", type=str, default=None, help="Limit checks to one domain in the meta file")
    parser.add_argument("--example_id", type=str, default=None, help="Limit checks to one example id")
    parser.add_argument("--check_env_reset", action="store_true", help="Run DesktopEnv.reset() + screenshot checks")
    parser.add_argument("--check_initial_evaluate", action="store_true", help="Run env.evaluate() after reset and record the score")
    parser.add_argument("--run_blackbox", action="store_true", help="Run each selected case through run_multienv_cua_blackbox.py")
    parser.add_argument("--provider_name", type=str, default="vmware", choices=["aws", "virtualbox", "vmware", "docker", "azure"])
    parser.add_argument("--region", type=str, default="us-east-1")
    parser.add_argument("--path_to_vm", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--client_password", type=str, default="")
    parser.add_argument("--screen_width", type=int, default=1920)
    parser.add_argument("--screen_height", type=int, default=1080)
    parser.add_argument("--env_ready_sleep", type=float, default=5.0)
    parser.add_argument("--model", type=str, default="cua-blackbox-case-acceptance")
    parser.add_argument("--max_steps", type=int, default=20)
    parser.add_argument("--log_level", type=str, default="INFO")
    parser.add_argument("--blackbox_result_dir", type=str, default="./results_cua_case_acceptance_blackbox")
    return parser.parse_args()


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: str, payload: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def _filter_rows(rows: list[dict[str, str]], domain: str | None, example_id: str | None) -> list[dict[str, str]]:
    filtered = rows
    if domain:
        filtered = [row for row in filtered if row["domain"] == domain]
    if example_id:
        filtered = [row for row in filtered if row["id"] == example_id]
    return filtered


def _case_path(cases_dir: str, cua_cases_dir: str, domain: str, case_id: str) -> str:
    return resolve_case_path(domain, case_id, cases_dir=cases_dir, cua_cases_dir=cua_cases_dir)


def _snapshot_name(provider_name: str, screen_width: int, screen_height: int) -> str:
    if provider_name == "aws":
        from desktop_env.providers.aws.manager import IMAGE_ID_MAP

        screen_size = (screen_width, screen_height)
        return IMAGE_ID_MAP["us-east-1"].get(screen_size, IMAGE_ID_MAP["us-east-1"][(1920, 1080)])
    return "init_state"


def _run_env_checks(args: argparse.Namespace, rows: list[dict[str, str]], cases_dir: str) -> list[dict[str, Any]]:
    if not args.check_env_reset and not args.check_initial_evaluate:
        return []

    from desktop_env.desktop_env import DesktopEnv

    env = DesktopEnv(
        path_to_vm=args.path_to_vm,
        action_space="pyautogui",
        provider_name=args.provider_name,
        region=args.region,
        snapshot_name=_snapshot_name(args.provider_name, args.screen_width, args.screen_height),
        screen_size=(args.screen_width, args.screen_height),
        headless=args.headless,
        os_type="Ubuntu",
        require_a11y_tree=False,
        enable_proxy=True,
        client_password=args.client_password,
    )

    checks: list[dict[str, Any]] = []
    try:
        for row in rows:
            domain = row["domain"]
            case_id = row["id"]
            case = _load_json(_case_path(cases_dir, args.cua_cases_dir, domain, case_id))
            record: dict[str, Any] = {
                "domain": domain,
                "id": case_id,
                "snapshot": row.get("snapshot"),
                "env_reset_passed": False,
                "screenshot_passed": False,
                "initial_evaluate_score": None,
                "passed": False,
                "errors": [],
            }
            try:
                obs = env.reset(task_config=case)
                if args.env_ready_sleep > 0:
                    time.sleep(args.env_ready_sleep)
                record["env_reset_passed"] = True
                screenshot = obs.get("screenshot") if isinstance(obs, dict) else None
                record["screenshot_passed"] = isinstance(screenshot, (bytes, bytearray)) and bool(screenshot)
                if not record["screenshot_passed"]:
                    record["errors"].append("reset observation has no screenshot")
                if args.check_initial_evaluate:
                    score = env.evaluate()
                    record["initial_evaluate_score"] = score
                record["passed"] = record["env_reset_passed"] and record["screenshot_passed"]
            except Exception as exc:
                record["errors"].append(str(exc))
            checks.append(record)
    finally:
        env.close()
    return checks


def _run_blackbox_case(args: argparse.Namespace, row: dict[str, str]) -> dict[str, Any]:
    command = [
        sys.executable,
        os.path.join(ROOT_DIR, "scripts", "python", "run_multienv_cua_blackbox.py"),
        "--provider_name",
        args.provider_name,
        "--action_space",
        "pyautogui",
        "--observation_type",
        "screenshot",
        "--test_all_meta_path",
        os.path.abspath(os.path.expanduser(os.path.expandvars(args.meta_path))),
        "--cua_cases_dir",
        os.path.abspath(os.path.expanduser(os.path.expandvars(args.cua_cases_dir))),
        "--domain",
        row["domain"],
        "--example_id",
        row["id"],
        "--model",
        args.model,
        "--num_envs",
        "1",
        "--max_steps",
        str(args.max_steps),
        "--screen_width",
        str(args.screen_width),
        "--screen_height",
        str(args.screen_height),
        "--env_ready_sleep",
        str(args.env_ready_sleep),
        "--result_dir",
        args.blackbox_result_dir,
        "--log_level",
        args.log_level,
    ]
    if args.path_to_vm:
        command.extend(["--path_to_vm", args.path_to_vm])
    if args.headless:
        command.append("--headless")
    if args.client_password:
        command.extend(["--client_password", args.client_password])

    started = time.time()
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {
        "domain": row["domain"],
        "id": row["id"],
        "passed": completed.returncode == 0,
        "exit_code": completed.returncode,
        "duration_seconds": time.time() - started,
        "command": command,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def main() -> int:
    args = config()
    result_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.result_dir)))
    meta_path = os.path.abspath(os.path.expanduser(os.path.expandvars(args.meta_path)))
    cases_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.cases_dir)))
    args.cua_cases_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.cua_cases_dir)))

    rows, static_errors = validate_cases(meta_path, cases_dir, args.cua_cases_dir)
    selected_rows = _filter_rows(rows, args.domain, args.example_id)
    selection_errors: list[str] = []
    if not selected_rows:
        selection_errors.append("no cases selected")

    env_checks = _run_env_checks(args, selected_rows, cases_dir) if not selection_errors else []
    blackbox_checks = [_run_blackbox_case(args, row) for row in selected_rows] if args.run_blackbox and not selection_errors else []

    passed = (
        not static_errors
        and not selection_errors
        and all(item.get("passed") for item in env_checks)
        and all(item.get("passed") for item in blackbox_checks)
    )
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "meta_path": meta_path,
        "cases_dir": cases_dir,
        "cua_cases_dir": args.cua_cases_dir,
        "selected_count": len(selected_rows),
        "selected_cases": selected_rows,
        "checks_requested": {
            "static": True,
            "env_reset": args.check_env_reset,
            "initial_evaluate": args.check_initial_evaluate,
            "blackbox": args.run_blackbox,
        },
        "static_errors": static_errors,
        "selection_errors": selection_errors,
        "env_checks": env_checks,
        "blackbox_checks": blackbox_checks,
        "passed": passed,
    }
    report_path = os.path.join(result_dir, "case_acceptance_report.json")
    _write_json(report_path, report)

    print(f"case_acceptance_report: {report_path}")
    print(f"selected_count: {len(selected_rows)}")
    if static_errors:
        print("static: FAIL")
        for error in static_errors:
            print(f"  {error}")
    else:
        print("static: PASS")
    for error in selection_errors:
        print(f"selection: FAIL {error}")
    for item in env_checks:
        status = "PASS" if item.get("passed") else "FAIL"
        print(f"{status} env {item['domain']}/{item['id']}")
        for error in item.get("errors") or []:
            print(f"  {error}")
    for item in blackbox_checks:
        status = "PASS" if item.get("passed") else "FAIL"
        print(f"{status} blackbox {item['domain']}/{item['id']} exit={item['exit_code']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
