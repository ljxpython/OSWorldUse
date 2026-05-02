from __future__ import annotations

import json
import math
from typing import Any


class ToolTranslationError(ValueError):
    pass


def _as_float(value: Any, name: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ToolTranslationError(f"{name} must be a number") from exc
    if not math.isfinite(out):
        raise ToolTranslationError(f"{name} must be finite")
    return out


def _as_int(value: Any, name: str) -> int:
    return int(round(_as_float(value, name)))


def _map_normalized(value: float, max_value: int | None) -> int:
    if max_value is None or max_value <= 0:
        return int(round(value))
    return int(round(value / 1000.0 * max_value))


def _bbox_center(args: dict[str, Any], key: str = "bbox", fmt_key: str = "bbox_format") -> tuple[int, int] | None:
    bbox = args.get(key)
    if bbox is None:
        return None
    if not isinstance(bbox, list | tuple) or len(bbox) != 4:
        raise ToolTranslationError(f"{key} must be a four-number array")
    a, b, c, d = [_as_float(v, key) for v in bbox]
    bbox_format = str(args.get(fmt_key) or "xyxy").lower()
    if bbox_format == "xywh":
        return int(round(a)), int(round(b))
    if bbox_format != "xyxy":
        raise ToolTranslationError(f"{fmt_key} must be xyxy or xywh")
    return int(round((a + c) / 2)), int(round((b + d) / 2))


def resolve_coords(args: dict[str, Any]) -> tuple[int, int]:
    if "x" in args and "y" in args:
        return _as_int(args["x"], "x"), _as_int(args["y"], "y")
    center = _bbox_center(args)
    if center is not None:
        return center
    raise ToolTranslationError("need x/y or bbox")


def resolve_optional_coords(args: dict[str, Any]) -> tuple[int, int] | None:
    if ("x" in args) != ("y" in args):
        raise ToolTranslationError("x and y must be provided together")
    if "x" in args and "y" in args:
        return _as_int(args["x"], "x"), _as_int(args["y"], "y")
    return _bbox_center(args)


def map_coords_to_screen(
    x: int,
    y: int,
    *,
    screen_size: tuple[int, int] | None = None,
    normalized_input: bool = False,
) -> tuple[int, int]:
    if not normalized_input:
        return x, y
    width: int | None = None
    height: int | None = None
    if screen_size is not None:
        width, height = int(screen_size[0]), int(screen_size[1])
    return _map_normalized(float(x), width), _map_normalized(float(y), height)


def map_args_to_screen(
    tool: str,
    args: dict[str, Any],
    *,
    screen_size: tuple[int, int] | None = None,
    normalized_input: bool = False,
) -> dict[str, Any]:
    mapped = dict(args)

    if tool in {"mouse_click", "mouse_right_click", "mouse_double_click", "mouse_move"}:
        coords = resolve_coords(mapped)
        x, y = map_coords_to_screen(coords[0], coords[1], screen_size=screen_size, normalized_input=normalized_input)
        mapped["x"] = x
        mapped["y"] = y
        mapped.pop("bbox", None)
        mapped.pop("bbox_format", None)
        return mapped

    if tool in {"press_mouse", "release_mouse"}:
        coords = resolve_optional_coords(mapped)
        if coords is not None:
            x, y = map_coords_to_screen(coords[0], coords[1], screen_size=screen_size, normalized_input=normalized_input)
            mapped["x"] = x
            mapped["y"] = y
            mapped.pop("bbox", None)
            mapped.pop("bbox_format", None)
        return mapped

    if tool == "mouse_scroll":
        coords = resolve_optional_coords(mapped)
        if coords is not None:
            x, y = map_coords_to_screen(coords[0], coords[1], screen_size=screen_size, normalized_input=normalized_input)
            mapped["x"] = x
            mapped["y"] = y
            mapped.pop("bbox", None)
            mapped.pop("bbox_format", None)
        return mapped

    if tool == "mouse_drag":
        from_x, from_y, to_x, to_y = resolve_drag_coords(mapped)
        fx, fy = map_coords_to_screen(from_x, from_y, screen_size=screen_size, normalized_input=normalized_input)
        tx, ty = map_coords_to_screen(to_x, to_y, screen_size=screen_size, normalized_input=normalized_input)
        mapped["fromX"] = fx
        mapped["fromY"] = fy
        mapped["toX"] = tx
        mapped["toY"] = ty
        mapped.pop("from_bbox", None)
        mapped.pop("from_bbox_format", None)
        mapped.pop("to_bbox", None)
        mapped.pop("to_bbox_format", None)
        return mapped

    return mapped


def resolve_drag_coords(args: dict[str, Any]) -> tuple[int, int, int, int]:
    if all(key in args for key in ("fromX", "fromY", "toX", "toY")):
        return (
            _as_int(args["fromX"], "fromX"),
            _as_int(args["fromY"], "fromY"),
            _as_int(args["toX"], "toX"),
            _as_int(args["toY"], "toY"),
        )

    start = _bbox_center(args, "from_bbox", "from_bbox_format")
    end = _bbox_center(args, "to_bbox", "to_bbox_format")
    if start is None or end is None:
        raise ToolTranslationError("need fromX/fromY/toX/toY or from_bbox/to_bbox")
    return start[0], start[1], end[0], end[1]


def _button(args: dict[str, Any]) -> str:
    button = str(args.get("button") or "left").lower()
    if button not in {"left", "right", "middle"}:
        raise ToolTranslationError("button must be left, right, or middle")
    return button


def _key(value: Any) -> str:
    key = str(value or "").strip().lower()
    if not key:
        raise ToolTranslationError("key must not be empty")
    aliases = {
        "return": "enter",
        "escape": "esc",
        "cmd": "ctrl",
        "command": "ctrl",
        "control": "ctrl",
        "option": "alt",
    }
    return aliases.get(key, key)


def _py_string(value: str) -> str:
    return repr(value)


def translate_tool_to_pyautogui(tool: str, args: dict[str, Any]) -> str | None:
    if tool == "mouse_click":
        x, y = resolve_coords(args)
        button = _button(args)
        return f"pyautogui.moveTo({x}, {y}); pyautogui.click(button={_py_string(button)})"

    if tool == "mouse_right_click":
        x, y = resolve_coords(args)
        return f"pyautogui.moveTo({x}, {y}); pyautogui.click(button='right')"

    if tool == "mouse_double_click":
        x, y = resolve_coords(args)
        return f"pyautogui.moveTo({x}, {y}); pyautogui.doubleClick(button='left')"

    if tool == "mouse_move":
        x, y = resolve_coords(args)
        return f"pyautogui.moveTo({x}, {y})"

    if tool == "mouse_drag":
        from_x, from_y, to_x, to_y = resolve_drag_coords(args)
        button = _button(args)
        return (
            f"pyautogui.moveTo({from_x}, {from_y}); "
            f"pyautogui.dragTo({to_x}, {to_y}, duration=0.5, button={_py_string(button)})"
        )

    if tool == "mouse_scroll":
        coords = resolve_optional_coords(args)
        clicks = _as_int(args.get("clicks", 0), "clicks")
        if clicks == 0:
            raise ToolTranslationError("clicks must be non-zero")
        prefix = ""
        if coords is not None:
            prefix = f"pyautogui.moveTo({coords[0]}, {coords[1]}); "
        return f"{prefix}pyautogui.scroll({clicks})"

    if tool == "press_mouse":
        coords = resolve_optional_coords(args)
        button = _button(args)
        prefix = f"pyautogui.moveTo({coords[0]}, {coords[1]}); " if coords else ""
        return f"{prefix}pyautogui.mouseDown(button={_py_string(button)})"

    if tool == "release_mouse":
        coords = resolve_optional_coords(args)
        button = _button(args)
        prefix = f"pyautogui.moveTo({coords[0]}, {coords[1]}); " if coords else ""
        return f"{prefix}pyautogui.mouseUp(button={_py_string(button)})"

    if tool in {"clipboard_type", "keyboard_type"}:
        text = str(args.get("text") or "")
        if not text:
            raise ToolTranslationError("text must not be empty")
        return (
            f"_cua_text = {_py_string(text)}; "
            "\ntry:\n"
            "    import pyperclip\n"
            "    pyperclip.copy(_cua_text)\n"
            "    pyautogui.hotkey('ctrl', 'v')\n"
            "except Exception:\n"
            "    pyautogui.write(_cua_text)\n"
        )

    if tool == "key_press":
        key = _key(args.get("key"))
        return f"pyautogui.press({_py_string(key)})"

    if tool == "hotkey":
        keys = args.get("keys")
        if not isinstance(keys, list) or not keys:
            raise ToolTranslationError("keys must be a non-empty array")
        normalized = [_key(k) for k in keys]
        joined = ", ".join(_py_string(k) for k in normalized)
        return f"pyautogui.hotkey({joined})"

    if tool == "wait":
        ms = max(0, _as_int(args.get("ms", 1000), "ms"))
        return f"time.sleep({ms / 1000.0})"

    return None


def tool_output(tool: str, args: dict[str, Any]) -> str:
    safe_args = json.dumps(args, ensure_ascii=False, sort_keys=True)
    return f"{tool} executed with args={safe_args}"
