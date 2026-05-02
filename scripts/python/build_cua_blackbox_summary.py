from __future__ import annotations

import argparse
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from osworld_cua_bridge.reporting import (
    SUMMARY_METADATA_FIELDS,
    blackbox_result_root,
    build_blackbox_summary,
    load_args_json,
    load_task_set_file,
    summary_metadata_from_args,
)


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild summary artifacts for CUA blackbox result directories")
    parser.add_argument("--result_dir", type=str, default="./results_cua_blackbox")
    parser.add_argument("--action_space", type=str, default="pyautogui")
    parser.add_argument("--observation_type", type=str, default="screenshot")
    parser.add_argument("--model", type=str, default="cua-blackbox")
    parser.add_argument("--test_all_meta_path", type=str, default="")
    parser.add_argument("--result_root", type=str, default="")
    return parser.parse_args()


def _flag_present(flag: str) -> bool:
    return any(arg == flag or arg.startswith(f"{flag}=") for arg in sys.argv[1:])


def _explicit_metadata_overrides(args: argparse.Namespace) -> dict[str, object]:
    overrides: dict[str, object] = {}
    for field in SUMMARY_METADATA_FIELDS:
        flag = f"--{field}"
        if _flag_present(flag):
            value = getattr(args, field, None)
            if value not in (None, ""):
                overrides[field] = value
    return overrides


def main() -> int:
    args = config()
    result_root = args.result_root or blackbox_result_root(args)
    saved_args = load_args_json(result_root)
    task_set_path = args.test_all_meta_path
    if not task_set_path and _flag_present("--result_root"):
        task_set_path = str(saved_args.get("test_all_meta_path") or "")
    task_set = load_task_set_file(task_set_path)

    metadata = summary_metadata_from_args(saved_args if saved_args else args)
    metadata.update(_explicit_metadata_overrides(args))
    summary = build_blackbox_summary(
        result_root,
        task_set=task_set,
        task_set_path=task_set_path,
        metadata=metadata,
    )
    totals = summary["totals"]
    summary_dir = os.path.join(result_root, "summary")
    print(f"summary_dir: {summary_dir}")
    print(
        "total={total_tasks} scored={scored_tasks} failed={failed_tasks} pending={pending_tasks} avg={average_score:.4f}".format(
            **totals
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
