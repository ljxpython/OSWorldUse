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
from scripts.python.build_cua_blackbox_report import build_report, write_outputs


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild summary artifacts for CUA blackbox result directories")
    parser.add_argument("--result_dir", type=str, default="./results_cua_blackbox")
    parser.add_argument("--action_space", type=str, default="pyautogui")
    parser.add_argument("--observation_type", type=str, default="screenshot")
    parser.add_argument("--model", type=str, default="cua-blackbox")
    parser.add_argument("--test_all_meta_path", type=str, default="")
    parser.add_argument("--result_root", type=str, default="")
    parser.add_argument("--build_report", action="store_true", help="Also build report/report.json, report.md and index.html")
    parser.add_argument("--report_output_dir", type=str, default="", help="Defaults to <result_root>/report")
    parser.add_argument("--report_title", type=str, default="CUA Blackbox Evaluation Report")
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
    if args.build_report:
        report_args = argparse.Namespace(
            result_root=result_root,
            result_dir=args.result_dir,
            action_space=args.action_space,
            observation_type=args.observation_type,
            model=args.model,
            output_dir=args.report_output_dir,
            title=args.report_title,
            smoke_report="",
            functional_report="",
            compatibility_report="",
            case_acceptance_report="",
        )
        paths = write_outputs(build_report(report_args))
        print(f"report_json: {paths['report_json']}")
        print(f"report_md: {paths['report_md']}")
        print(f"index_html: {paths['index_html']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
