from __future__ import annotations

import dataclasses
import datetime
from typing import Any


BRIDGE_PROTOCOL_VERSION = "bridge-v1"

SUPPORTED_TOOLS = {
    "screenshot",
    "mouse_click",
    "mouse_right_click",
    "mouse_double_click",
    "mouse_move",
    "mouse_drag",
    "mouse_scroll",
    "press_mouse",
    "release_mouse",
    "clipboard_type",
    "keyboard_type",
    "key_press",
    "hotkey",
    "wait",
    "get_screen_size",
    "done",
}

DISABLED_TOOLS = {
    "shell_exec",
    "shell_sh",
    "officecli",
    "record_info",
    "read_record",
    "wait_for_user",
    "app_open",
    "osascript_exec",
    "get_cursor_position",
}


@dataclasses.dataclass(frozen=True)
class BridgeRequest:
    run_id: str
    req_id: str
    tool: str
    args: dict[str, Any]


class BridgeProtocolError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def parse_request(payload: dict[str, Any]) -> BridgeRequest:
    if not isinstance(payload, dict):
        raise BridgeProtocolError("BAD_REQUEST", "request body must be a JSON object")

    run_id = str(payload.get("runId") or "").strip()
    req_id = str(payload.get("reqId") or "").strip()
    tool = str(payload.get("tool") or "").strip()
    args = payload.get("args")

    if not run_id:
        raise BridgeProtocolError("BAD_REQUEST", "missing runId")
    if not req_id:
        raise BridgeProtocolError("BAD_REQUEST", "missing reqId")
    if not tool:
        raise BridgeProtocolError("BAD_REQUEST", "missing tool")
    if args is None:
        args = {}
    if not isinstance(args, dict):
        raise BridgeProtocolError("BAD_REQUEST", "args must be an object")
    if tool in DISABLED_TOOLS:
        raise BridgeProtocolError("UNSUPPORTED_TOOL", f"tool disabled in first phase: {tool}", {"tool": tool})
    if tool not in SUPPORTED_TOOLS:
        raise BridgeProtocolError("UNSUPPORTED_TOOL", f"unsupported tool: {tool}", {"tool": tool})

    return BridgeRequest(run_id=run_id, req_id=req_id, tool=tool, args=args)


def ok(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "payload": payload}


def error(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "details": {
                "timestamp": now_iso(),
                **(details or {}),
            },
        },
    }

