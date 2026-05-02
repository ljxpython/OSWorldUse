from __future__ import annotations

"""Deprecated historical translator for the mm_agents/cua adapter route.

The current supported path is the blackbox bridge tool translator under
osworld_cua_bridge/tool_translator.py.
"""

import ast
import json
from dataclasses import asdict
from typing import Any, Iterable, List, Sequence

from mm_agents.cua.types import CUAAction


class CUAActionTranslationError(ValueError):
    pass


def _py_string(value: str) -> str:
    return repr(value)


def _coerce_number(value: Any, name: str) -> int:
    try:
        return int(round(float(value)))
    except (TypeError, ValueError) as exc:
        raise CUAActionTranslationError(f"{name} must be numeric") from exc


def _coerce_button(value: Any) -> str:
    button = str(value or "left").lower()
    if button not in {"left", "right", "middle"}:
        raise CUAActionTranslationError("button must be left, right, or middle")
    return button


def _coerce_keys(value: Any) -> List[str]:
    if isinstance(value, str):
        items = [part.strip() for part in value.replace("+", " ").split() if part.strip()]
    elif isinstance(value, Sequence):
        items = [str(item).strip() for item in value if str(item).strip()]
    else:
        raise CUAActionTranslationError("keys must be a string or array")

    if not items:
        raise CUAActionTranslationError("keys must not be empty")

    aliases = {
        "return": "enter",
        "escape": "esc",
        "command": "ctrl",
        "cmd": "ctrl",
        "control": "ctrl",
        "option": "alt",
        "super": "win",
    }
    return [aliases.get(item.lower(), item.lower()) for item in items]


def _translate_click(action: CUAAction) -> str:
    x = action.args.get("x")
    y = action.args.get("y")
    if x is None or y is None:
        raise CUAActionTranslationError("click requires x and y")
    button = _coerce_button(action.args.get("button"))
    num_clicks = int(action.args.get("clicks") or action.args.get("num_clicks") or 1)
    if num_clicks <= 0:
        raise CUAActionTranslationError("clicks must be positive")
    return (
        f"import pyautogui\n"
        f"pyautogui.moveTo({_coerce_number(x, 'x')}, {_coerce_number(y, 'y')})\n"
        f"pyautogui.click(button={_py_string(button)}, clicks={num_clicks})"
    )


def _translate_double_click(action: CUAAction) -> str:
    x = action.args.get("x")
    y = action.args.get("y")
    if x is None or y is None:
        raise CUAActionTranslationError("double_click requires x and y")
    button = _coerce_button(action.args.get("button"))
    return (
        f"import pyautogui\n"
        f"pyautogui.moveTo({_coerce_number(x, 'x')}, {_coerce_number(y, 'y')})\n"
        f"pyautogui.doubleClick(button={_py_string(button)})"
    )


def _translate_move(action: CUAAction) -> str:
    x = action.args.get("x")
    y = action.args.get("y")
    if x is None or y is None:
        raise CUAActionTranslationError("move requires x and y")
    return f"import pyautogui\npyautogui.moveTo({_coerce_number(x, 'x')}, {_coerce_number(y, 'y')})"


def _translate_drag(action: CUAAction) -> str:
    if all(key in action.args for key in ("fromX", "fromY", "toX", "toY")):
        from_x = _coerce_number(action.args["fromX"], "fromX")
        from_y = _coerce_number(action.args["fromY"], "fromY")
        to_x = _coerce_number(action.args["toX"], "toX")
        to_y = _coerce_number(action.args["toY"], "toY")
    else:
        path = action.args.get("path")
        if not isinstance(path, Sequence) or len(path) < 2:
            raise CUAActionTranslationError("drag requires from/to coordinates or path")
        start = path[0]
        end = path[-1]
        if isinstance(start, dict) and isinstance(end, dict) and "x" in start and "y" in start and "x" in end and "y" in end:
            from_x = _coerce_number(start["x"], "fromX")
            from_y = _coerce_number(start["y"], "fromY")
            to_x = _coerce_number(end["x"], "toX")
            to_y = _coerce_number(end["y"], "toY")
        else:
            raise CUAActionTranslationError("drag path must contain coordinate objects")
    button = _coerce_button(action.args.get("button"))
    return (
        f"import pyautogui\n"
        f"pyautogui.moveTo({from_x}, {from_y})\n"
        f"pyautogui.dragTo({to_x}, {to_y}, duration=0.5, button={_py_string(button)})"
    )


def _translate_scroll(action: CUAAction) -> str:
    clicks = action.args.get("clicks")
    if clicks is None:
        clicks = action.args.get("scroll_y")
    if clicks is None:
        raise CUAActionTranslationError("scroll requires clicks or scroll_y")
    clicks_int = _coerce_number(clicks, "clicks")
    x = action.args.get("x")
    y = action.args.get("y")
    prefix = ""
    if x is not None and y is not None:
        prefix = f"pyautogui.moveTo({_coerce_number(x, 'x')}, {_coerce_number(y, 'y')}); "
    return f"{prefix}pyautogui.scroll({clicks_int})"


def _translate_type(action: CUAAction) -> str:
    text = action.args.get("text")
    if text is None:
        text = action.args.get("content")
    if text is None:
        raise CUAActionTranslationError("type requires text or content")
    return (
        "import pyautogui\n"
        f"_cua_text = {_py_string(str(text))}\n"
        "try:\n"
        "    import pyperclip\n"
        "    pyperclip.copy(_cua_text)\n"
        "    pyautogui.hotkey('ctrl', 'v')\n"
        "except Exception:\n"
        "    pyautogui.write(_cua_text)"
    )


def _translate_hotkey(action: CUAAction) -> str:
    keys = action.args.get("keys")
    if keys is None and action.args.get("key") is not None:
        keys = [action.args["key"]]
    normalized = _coerce_keys(keys)
    return f"import pyautogui\npyautogui.hotkey({', '.join(_py_string(k) for k in normalized)})"


def _translate_key_press(action: CUAAction) -> str:
    key = action.args.get("key")
    if key is None:
        keys = action.args.get("keys")
        if isinstance(keys, Sequence) and keys:
            key = keys[0]
    if key is None:
        raise CUAActionTranslationError("key_press requires key or keys")
    normalized = _coerce_keys([key])
    return f"import pyautogui\npyautogui.press({_py_string(normalized[0])})"


class CUAActionTranslator:
    """Deprecated historical action translator.

    Retained as reference only. The supported runtime path uses
    osworld_cua_bridge.tool_translator instead.
    """

    def __init__(self, platform: str = "ubuntu"):
        self.platform = platform

    def to_osworld_action(self, action: CUAAction) -> str:
        kind = str(action.kind or "").strip().lower()
        if not kind:
            raise CUAActionTranslationError("action kind is empty")

        if kind in {"wait", "screenshot"}:
            return "WAIT"
        if kind in {"done", "terminate"}:
            return "DONE"
        if kind in {"fail", "infeasible"}:
            return "FAIL"
        if kind in {"click", "mouse_click"}:
            return _translate_click(action)
        if kind in {"double_click", "mouse_double_click"}:
            return _translate_double_click(action)
        if kind in {"move", "mouse_move"}:
            return _translate_move(action)
        if kind in {"drag", "mouse_drag"}:
            return _translate_drag(action)
        if kind in {"scroll", "mouse_scroll"}:
            return _translate_scroll(action)
        if kind in {"type", "keyboard_type", "clipboard_type"}:
            return _translate_type(action)
        if kind == "hotkey":
            return _translate_hotkey(action)
        if kind in {"key_press", "keypress", "press"}:
            return _translate_key_press(action)

        raise CUAActionTranslationError(f"unsupported action kind: {kind}")


def normalize_action_payload(payload: Any) -> CUAAction:
    if isinstance(payload, CUAAction):
        return payload
    if isinstance(payload, dict):
        kind = payload.get("kind") or payload.get("type") or payload.get("action") or payload.get("name")
        if not kind:
            raise CUAActionTranslationError("missing action kind")
        raw_args = payload.get("args")
        if raw_args is None and "params" in payload:
            raw_args = payload["params"]
        if raw_args is None:
            raw_args = {k: v for k, v in payload.items() if k not in {"kind", "type", "action", "name", "raw_text", "natural_language", "args", "params"}}
        if not isinstance(raw_args, dict):
            raise CUAActionTranslationError("action args must be an object")
        return CUAAction(
            kind=str(kind),
            args=dict(raw_args),
            raw_text=str(payload.get("raw_text") or payload.get("raw") or ""),
            natural_language=str(payload.get("natural_language") or payload.get("description") or ""),
        )
    raise CUAActionTranslationError("unsupported action payload type")


def parse_action_text(text: str) -> CUAAction:
    trimmed = text.strip()
    if not trimmed:
        raise CUAActionTranslationError("empty action text")
    if trimmed.lower() in {"wait", "done", "fail"}:
        return CUAAction(kind=trimmed.upper(), raw_text=text)
    if trimmed.startswith("```"):
        fenced = trimmed
        fenced = fenced.removeprefix("```json").removeprefix("```python").removeprefix("```code").removeprefix("```")
        fenced = fenced.strip()
        if fenced.endswith("```"):
            fenced = fenced[:-3].strip()
        trimmed = fenced
    try:
        parsed = json.loads(trimmed)
        if isinstance(parsed, dict):
            return normalize_action_payload(parsed)
    except Exception:
        pass
    try:
        parsed = ast.literal_eval(trimmed)
        if isinstance(parsed, dict):
            return normalize_action_payload(parsed)
    except Exception:
        pass
    raise CUAActionTranslationError("unable to parse action text")
