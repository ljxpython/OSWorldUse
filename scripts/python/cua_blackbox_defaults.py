from __future__ import annotations

import os


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DEFAULT_CASES_DIR = os.path.join(ROOT_DIR, "evaluation_examples", "examples")
CUA_BLACKBOX_DIR = os.path.join(ROOT_DIR, "evaluation_examples", "cua_blackbox")
CUA_BLACKBOX_CASES_DIR = os.path.join(CUA_BLACKBOX_DIR, "cases")
CUA_BLACKBOX_META_PATH = os.path.join(CUA_BLACKBOX_DIR, "suites", "regression.json")
LEGACY_CUA_REGRESSION_META_PATH = os.path.join(
    ROOT_DIR, "evaluation_examples", "test_cua_regression.json"
)


def default_cua_regression_meta_path() -> str:
    if os.path.exists(CUA_BLACKBOX_META_PATH):
        return CUA_BLACKBOX_META_PATH
    return LEGACY_CUA_REGRESSION_META_PATH
