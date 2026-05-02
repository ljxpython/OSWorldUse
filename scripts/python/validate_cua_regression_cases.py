from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from desktop_env.evaluators import getters, metrics

DEFAULT_META_PATH = os.path.join(ROOT_DIR, "evaluation_examples", "test_cua_regression.json")
DEFAULT_CASES_DIR = os.path.join(ROOT_DIR, "evaluation_examples", "examples")


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the fixed CUA blackbox regression task set")
    parser.add_argument("--meta_path", type=str, default=DEFAULT_META_PATH)
    parser.add_argument("--cases_dir", type=str, default=DEFAULT_CASES_DIR)
    parser.add_argument("--report_path", type=str, default=None)
    return parser.parse_args()


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _validate_meta(meta: Any) -> dict[str, list[str]]:
    if not isinstance(meta, dict) or not meta:
        raise ValueError("meta file must be a non-empty JSON object")

    normalized: dict[str, list[str]] = {}
    for domain, items in meta.items():
        if not isinstance(domain, str) or not domain:
            raise ValueError(f"invalid domain key: {domain!r}")
        if not isinstance(items, list) or not items:
            raise ValueError(f"domain {domain!r} must map to a non-empty list")
        normalized[domain] = [str(item) for item in items]
    return normalized


def _validate_case_payload(domain: str, case_id: str, payload: Any, path: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return [f"{domain}/{case_id}: case file is not a JSON object: {path}"]

    required_string_fields = ("id", "snapshot", "instruction")
    for field in required_string_fields:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{domain}/{case_id}: missing or empty {field}")

    if payload.get("id") != case_id:
        errors.append(f"{domain}/{case_id}: case id does not match meta/file id")

    file_stem = os.path.splitext(os.path.basename(path))[0]
    if file_stem != case_id:
        errors.append(f"{domain}/{case_id}: filename does not match case id")

    related_apps = payload.get("related_apps")
    if not isinstance(related_apps, list) or not related_apps:
        errors.append(f"{domain}/{case_id}: related_apps must be a non-empty list")

    evaluator = payload.get("evaluator")
    if not isinstance(evaluator, dict):
        errors.append(f"{domain}/{case_id}: evaluator must be an object")
        return errors

    func = evaluator.get("func")
    if not isinstance(func, (str, list)) or (isinstance(func, list) and not func):
        errors.append(f"{domain}/{case_id}: evaluator.func must be a non-empty string or list")
    elif func == "infeasible":
        errors.append(f"{domain}/{case_id}: infeasible case should not be in the regression suite")
    else:
        for func_name in _as_string_list(func):
            if func_name == "infeasible":
                errors.append(f"{domain}/{case_id}: infeasible case should not be in the regression suite")
            elif not hasattr(metrics, func_name):
                errors.append(f"{domain}/{case_id}: evaluator metric not found: {func_name}")

    if "result" not in evaluator:
        errors.append(f"{domain}/{case_id}: evaluator.result is required for regression validation")
    else:
        for getter_type in _extract_getter_types(evaluator.get("result")):
            if not _getter_exists(getter_type):
                errors.append(f"{domain}/{case_id}: evaluator result getter not found: {getter_type}")

    for getter_type in _extract_getter_types(evaluator.get("expected")):
        if getter_type == "rule":
            continue
        if not _getter_exists(getter_type):
            errors.append(f"{domain}/{case_id}: evaluator expected getter not found: {getter_type}")

    return errors


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str) and item.strip()]
    return []


def _extract_getter_types(value: Any) -> list[str]:
    if isinstance(value, dict):
        getter_type = value.get("type")
        return [str(getter_type)] if isinstance(getter_type, str) and getter_type.strip() else []
    if isinstance(value, list):
        types: list[str] = []
        for item in value:
            types.extend(_extract_getter_types(item))
        return types
    return []


def _getter_exists(getter_type: str) -> bool:
    getter_name = f"get_{getter_type}"
    return hasattr(getters, getter_name)


def validate_cases(meta_path: str, cases_dir: str) -> tuple[list[dict[str, str]], list[str]]:
    meta = _validate_meta(_load_json(meta_path))
    rows: list[dict[str, str]] = []
    errors: list[str] = []

    for domain in sorted(meta):
        for case_id in meta[domain]:
            case_path = os.path.join(cases_dir, domain, f"{case_id}.json")
            if not os.path.exists(case_path):
                errors.append(f"{domain}/{case_id}: case file not found: {case_path}")
                continue

            try:
                payload = _load_json(case_path)
            except Exception as exc:
                errors.append(f"{domain}/{case_id}: failed to load case file: {exc}")
                continue

            errors.extend(_validate_case_payload(domain, case_id, payload, case_path))
            rows.append(
                {
                    "domain": domain,
                    "id": case_id,
                    "snapshot": str(payload.get("snapshot", "")),
                    "related_apps": ",".join(str(item) for item in payload.get("related_apps", [])),
                    "instruction": str(payload.get("instruction", "")).strip(),
                }
            )
    return rows, errors


def main() -> int:
    args = config()
    meta_path = os.path.abspath(os.path.expanduser(os.path.expandvars(args.meta_path)))
    cases_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(args.cases_dir)))

    rows, errors = validate_cases(meta_path, cases_dir)
    report = {
        "meta_path": meta_path,
        "cases_dir": cases_dir,
        "task_count": len(rows),
        "rows": rows,
        "errors": errors,
        "passed": not errors,
    }
    if args.report_path:
        report_path = os.path.abspath(os.path.expanduser(os.path.expandvars(args.report_path)))
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"meta_path: {meta_path}")
    print(f"cases_dir: {cases_dir}")
    print(f"task_count: {len(rows)}")
    for row in rows:
        print(f"- {row['domain']}/{row['id']} [{row['snapshot']}] {row['instruction']}")

    if errors:
        print("validation: FAIL")
        for error in errors:
            print(f"  {error}")
        return 1

    print("validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
