from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DEFAULT_META_PATH = os.path.join(ROOT_DIR, "evaluation_examples", "test_cua_regression.json")
DEFAULT_CASES_DIR = os.path.join(ROOT_DIR, "evaluation_examples", "examples")


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the fixed CUA blackbox regression task set")
    parser.add_argument("--meta_path", type=str, default=DEFAULT_META_PATH)
    parser.add_argument("--cases_dir", type=str, default=DEFAULT_CASES_DIR)
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

    if "result" not in evaluator:
        errors.append(f"{domain}/{case_id}: evaluator.result is required for regression validation")

    return errors


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
