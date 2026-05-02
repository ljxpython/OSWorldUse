from __future__ import annotations

"""Deprecated historical data types for the mm_agents/cua adapter route."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


BRIDGE_PROTOCOL_VERSION = "bridge-v1"
DEFAULT_ADAPTER_VERSION = "v1"
DEFAULT_EVAL_PROFILE = "ubuntu-screenshot-pyautogui-v1"


@dataclass(slots=True)
class CUAAction:
    kind: str
    args: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    natural_language: str = ""


@dataclass(slots=True)
class CUAPrediction:
    response_text: str
    actions: List[str] = field(default_factory=list)
    parsed_actions: List[CUAAction] = field(default_factory=list)
    terminal_signal: Optional[str] = None
    state_correct: bool = False
    debug: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CUARuntimeMetadata:
    osworld_version: str
    cua_version: str
    adapter_version: str
    bridge_protocol_version: str
    eval_profile: str
    screen_size: Tuple[int, int]
    model: str
    normalized_input: bool
    cua_repo_path: str = ""
