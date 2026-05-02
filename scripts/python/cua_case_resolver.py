from __future__ import annotations

import os


def resolve_case_path(
    domain: str,
    case_id: str,
    *,
    cases_dir: str,
    cua_cases_dir: str | None = None,
) -> str:
    primary_path = os.path.join(cases_dir, domain, f"{case_id}.json")
    if os.path.exists(primary_path):
        return primary_path

    if cua_cases_dir:
        cua_path = os.path.join(cua_cases_dir, domain, f"{case_id}.json")
        if os.path.exists(cua_path):
            return cua_path

    return primary_path
