from __future__ import annotations

import argparse
import os
import subprocess
import sys


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RUNNER = os.path.join(ROOT_DIR, "scripts", "python", "run_multienv_cua_blackbox.py")
DEFAULT_META_PATH = os.path.join(ROOT_DIR, "evaluation_examples", "test_cua_regression.json")
DEFAULT_CONFIG_PATH = "/Users/bytedance/PycharmProjects/work/xua/runtime/agents/cua/config/local.json"


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the fixed CUA blackbox regression suite on OSWorld")
    parser.add_argument("--provider_name", type=str, default="vmware")
    parser.add_argument("--path_to_vm", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--model", type=str, default="cua-blackbox-regression")
    parser.add_argument("--result_dir", type=str, default="./results_cua_regression")
    parser.add_argument("--test_all_meta_path", type=str, default=DEFAULT_META_PATH)
    parser.add_argument("--domain", type=str, default="all")
    parser.add_argument("--example_id", type=str, default=None)
    parser.add_argument("--num_envs", type=int, default=1)
    parser.add_argument("--max_steps", type=int, default=20)
    parser.add_argument("--screen_width", type=int, default=1920)
    parser.add_argument("--screen_height", type=int, default=1080)
    parser.add_argument("--env_ready_sleep", type=float, default=10)
    parser.add_argument("--settle_sleep", type=float, default=5)
    parser.add_argument("--cua_bin", type=str, default=None)
    parser.add_argument("--cua_repo_root", type=str, default=None)
    parser.add_argument("--cua_config_path", type=str, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--cua_runs_dir", type=str, default=None)
    parser.add_argument("--cua_node_id", type=str, default=None)
    parser.add_argument("--cua_max_duration_ms", type=int, default=420000)
    parser.add_argument("--cua_max_step_duration_ms", type=int, default=120000)
    parser.add_argument("--cua_timeout_grace_seconds", type=float, default=60)
    parser.add_argument("--cua_version", type=str, default=None)
    parser.add_argument("--openclaw_bin", type=str, default=None)
    parser.add_argument("--log_level", type=str, default="INFO")
    parser.add_argument("--dry_run", action="store_true")
    parser.add_argument("--cua_extra_args", nargs=argparse.REMAINDER, default=None)
    return parser.parse_args()


def build_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        RUNNER,
        "--provider_name",
        args.provider_name,
        "--action_space",
        "pyautogui",
        "--observation_type",
        "screenshot",
        "--test_all_meta_path",
        args.test_all_meta_path,
        "--model",
        args.model,
        "--result_dir",
        args.result_dir,
        "--num_envs",
        str(args.num_envs),
        "--max_steps",
        str(args.max_steps),
        "--screen_width",
        str(args.screen_width),
        "--screen_height",
        str(args.screen_height),
        "--env_ready_sleep",
        str(args.env_ready_sleep),
        "--settle_sleep",
        str(args.settle_sleep),
        "--cua_config_path",
        args.cua_config_path,
        "--cua_max_duration_ms",
        str(args.cua_max_duration_ms),
        "--cua_max_step_duration_ms",
        str(args.cua_max_step_duration_ms),
        "--cua_timeout_grace_seconds",
        str(args.cua_timeout_grace_seconds),
        "--log_level",
        args.log_level,
    ]

    if args.path_to_vm:
        command.extend(["--path_to_vm", args.path_to_vm])
    if args.headless:
        command.append("--headless")
    if args.domain != "all":
        command.extend(["--domain", args.domain])
    if args.example_id:
        command.extend(["--example_id", args.example_id])
    if args.cua_bin:
        command.extend(["--cua_bin", args.cua_bin])
    if args.cua_repo_root:
        command.extend(["--cua_repo_root", args.cua_repo_root])
    if args.cua_runs_dir:
        command.extend(["--cua_runs_dir", args.cua_runs_dir])
    if args.cua_node_id:
        command.extend(["--cua_node_id", args.cua_node_id])
    if args.cua_version:
        command.extend(["--cua_version", args.cua_version])
    if args.openclaw_bin:
        command.extend(["--openclaw_bin", args.openclaw_bin])
    if args.cua_extra_args:
        command.append("--cua_extra_args")
        command.extend(args.cua_extra_args)
    return command


def main() -> int:
    args = config()
    command = build_command(args)
    print("command:")
    print(" ".join(command))
    if args.dry_run:
        return 0
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
