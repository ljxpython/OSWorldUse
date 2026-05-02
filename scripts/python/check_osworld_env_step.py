from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)


logger = logging.getLogger("desktopenv.env_step_check")


@dataclass
class StepCheck:
    id: str
    action: str
    passed: bool
    duration_seconds: float
    done: bool
    info: dict[str, Any]
    screenshot_path: str | None = None
    failure_reason: str | None = None


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify DesktopEnv.step() on a real OSWorld environment")
    parser.add_argument("--provider_name", type=str, default="vmware", choices=["aws", "virtualbox", "vmware", "docker", "azure"])
    parser.add_argument("--region", type=str, default="us-east-1")
    parser.add_argument("--path_to_vm", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--client_password", type=str, default="")
    parser.add_argument("--screen_width", type=int, default=1920)
    parser.add_argument("--screen_height", type=int, default=1080)
    parser.add_argument("--snapshot_name", type=str, default="init_state")
    parser.add_argument("--result_dir", type=str, default="./results_osworld_env_step")
    parser.add_argument("--env_ready_sleep", type=float, default=5.0)
    parser.add_argument("--step_pause", type=float, default=0.5)
    parser.add_argument("--no_reset", action="store_true", help="Do not call env.reset() before step checks")
    parser.add_argument(
        "--log_level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
    )
    return parser.parse_args()


def setup_logging(result_dir: str, level: str) -> None:
    os.makedirs(result_dir, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    root.handlers.clear()

    formatter = logging.Formatter("[%(asctime)s %(levelname)s %(name)s] %(message)s")
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(getattr(logging, level.upper()))
    stdout_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(os.path.join(result_dir, "runtime.log"), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)
    root.addHandler(file_handler)


def save_screenshot(obs: dict[str, Any], path: str) -> tuple[str | None, str | None]:
    screenshot = obs.get("screenshot") if isinstance(obs, dict) else None
    if not screenshot:
        return None, "observation has no screenshot"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as file:
        file.write(screenshot)
    return path, None


def run_step(env: Any, action: str, check_id: str, result_dir: str, pause: float) -> StepCheck:
    started = time.time()
    try:
        obs, _reward, done, info = env.step(action, pause=pause)
        duration = time.time() - started
        screenshot_path, screenshot_error = save_screenshot(
            obs,
            os.path.join(result_dir, "screenshots", f"{check_id}.png"),
        )
        passed = isinstance(obs, dict) and screenshot_error is None and isinstance(info, dict)
        return StepCheck(
            id=check_id,
            action=action,
            passed=passed,
            duration_seconds=duration,
            done=bool(done),
            info=info if isinstance(info, dict) else {"raw_info": str(info)},
            screenshot_path=screenshot_path,
            failure_reason=screenshot_error,
        )
    except Exception as exc:
        logger.exception("env.step check failed: %s", check_id)
        return StepCheck(
            id=check_id,
            action=action,
            passed=False,
            duration_seconds=time.time() - started,
            done=False,
            info={},
            failure_reason=str(exc),
        )


def write_report(result_dir: str, args: argparse.Namespace, checks: list[StepCheck]) -> str:
    report = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "result_dir": result_dir,
        "passed": all(check.passed for check in checks),
        "total": len(checks),
        "passed_count": sum(1 for check in checks if check.passed),
        "failed_count": sum(1 for check in checks if not check.passed),
        "args": vars(args),
        "checks": [asdict(check) for check in checks],
    }
    report_path = os.path.join(result_dir, "env_step_report.json")
    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    return report_path


def run() -> int:
    args = config()
    result_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.result_dir)))
    setup_logging(result_dir, args.log_level)

    from desktop_env.desktop_env import DesktopEnv

    env = None
    checks: list[StepCheck] = []
    try:
        env = DesktopEnv(
            path_to_vm=args.path_to_vm,
            action_space="pyautogui",
            provider_name=args.provider_name,
            region=args.region,
            snapshot_name=args.snapshot_name,
            screen_size=(args.screen_width, args.screen_height),
            headless=args.headless,
            os_type="Ubuntu",
            require_a11y_tree=False,
            enable_proxy=False,
            client_password=args.client_password,
        )
        if not args.no_reset:
            logger.info("Resetting environment before env.step checks")
            env.reset()
        if args.env_ready_sleep > 0:
            logger.info("Waiting %.1f seconds for VM readiness", args.env_ready_sleep)
            time.sleep(args.env_ready_sleep)

        checks.append(run_step(env, "WAIT", "wait", result_dir, args.step_pause))
        checks.append(
            run_step(
                env,
                f"pyautogui.moveTo({args.screen_width // 2}, {args.screen_height // 2}); pyautogui.click()",
                "pyautogui_click",
                result_dir,
                args.step_pause,
            )
        )
        report_path = write_report(result_dir, args, checks)

        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"{status} {check.id}")
            if check.failure_reason:
                print(f"  {check.failure_reason}")
        print(f"report: {report_path}")
        return 0 if all(check.passed for check in checks) else 1
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                logger.exception("Failed to close DesktopEnv")


if __name__ == "__main__":
    raise SystemExit(run())
