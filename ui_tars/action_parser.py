from __future__ import annotations

import re
from typing import Any


FUNCTION_BLOCK_RE = re.compile(
    r"<function[^<>=]*=([A-Za-z0-9_]+)>(.*?)</function[^>]*>",
    re.DOTALL,
)
PARAMETER_BLOCK_RE = re.compile(
    r"<parameter[^<>=]*=([A-Za-z0-9_]+)>(.*?)</parameter[^>]*>",
    re.DOTALL,
)
POINT_RE = re.compile(
    r"<point>\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*</point>",
    re.DOTALL,
)


def parse_xml_action(text: str, tool_schemas: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return parse_xml_action_v3(text, tool_schemas)


def parse_xml_action_v3(text: str, tool_schemas: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    schema_map = _build_schema_map(tool_schemas)
    parsed_actions: list[dict[str, Any]] = []

    for function_name, body in FUNCTION_BLOCK_RE.findall(text):
        parameters: dict[str, str] = {}
        for parameter_name, raw_value in PARAMETER_BLOCK_RE.findall(body):
            value = raw_value.strip()
            parameters[parameter_name] = value

        if schema_map:
            expected = schema_map.get(function_name)
            if expected is None:
                continue
            required = expected.get("required", [])
            if any(name not in parameters for name in required):
                continue

        parsed_actions.append(
            {
                "function": function_name,
                "parameters": parameters,
            }
        )

    return parsed_actions


def parsing_response_to_pyautogui_code(
    responses: dict[str, Any] | list[dict[str, Any]],
    image_height: int,
    image_width: int,
    input_swap: bool = True,
) -> str:
    if isinstance(responses, dict):
        responses = [responses]

    lines = [
        "import pyautogui",
        "import time",
    ]

    needs_pyperclip = any(
        response.get("action_type") == "type" and response.get("action_inputs", {}).get("content")
        for response in responses
    )
    if needs_pyperclip and input_swap:
        lines.append("import pyperclip")

    for index, response in enumerate(responses):
        if index > 0:
            lines.append("time.sleep(0.5)")

        action_type = response.get("action_type")
        action_inputs = response.get("action_inputs", {})

        if action_type in {"click", "left_single"}:
            x, y = _point_to_coordinates(action_inputs.get("point"), image_width, image_height)
            lines.append(f"pyautogui.click({x}, {y}, button='left')")
        elif action_type == "left_double":
            x, y = _point_to_coordinates(action_inputs.get("point"), image_width, image_height)
            lines.append(f"pyautogui.doubleClick({x}, {y}, button='left')")
        elif action_type == "right_single":
            x, y = _point_to_coordinates(action_inputs.get("point"), image_width, image_height)
            lines.append(f"pyautogui.click({x}, {y}, button='right')")
        elif action_type == "move_to":
            x, y = _point_to_coordinates(action_inputs.get("point"), image_width, image_height)
            lines.append(f"pyautogui.moveTo({x}, {y})")
        elif action_type == "drag":
            start_x, start_y = _point_to_coordinates(
                action_inputs.get("start_point"), image_width, image_height
            )
            end_x, end_y = _point_to_coordinates(
                action_inputs.get("end_point"), image_width, image_height
            )
            lines.append(f"pyautogui.moveTo({start_x}, {start_y})")
            lines.append(f"pyautogui.dragTo({end_x}, {end_y}, duration=0.5)")
        elif action_type == "scroll":
            direction = str(action_inputs.get("direction", "down")).strip().lower()
            amount = 5 if direction in {"up", "left"} else -5
            point = action_inputs.get("point")
            if point:
                x, y = _point_to_coordinates(point, image_width, image_height)
                lines.append(f"pyautogui.scroll({amount}, x={x}, y={y})")
            else:
                lines.append(f"pyautogui.scroll({amount})")
        elif action_type == "hotkey":
            keys = [_normalize_key(key) for key in str(action_inputs.get("key", "")).split() if key]
            if keys:
                rendered_keys = ", ".join(repr(key) for key in keys)
                lines.append(f"pyautogui.hotkey({rendered_keys})")
        elif action_type in {"press", "keydown"}:
            key = _normalize_key(action_inputs.get("key", ""))
            if key:
                lines.append(f"pyautogui.keyDown({key!r})")
        elif action_type in {"release", "keyup"}:
            key = _normalize_key(action_inputs.get("key", ""))
            if key:
                lines.append(f"pyautogui.keyUp({key!r})")
        elif action_type == "mouse_down":
            button = _normalize_button(action_inputs.get("button", "left"))
            point = action_inputs.get("point")
            if point:
                x, y = _point_to_coordinates(point, image_width, image_height)
                lines.append(f"pyautogui.mouseDown({x}, {y}, button={button!r})")
            else:
                lines.append(f"pyautogui.mouseDown(button={button!r})")
        elif action_type == "mouse_up":
            button = _normalize_button(action_inputs.get("button", "left"))
            point = action_inputs.get("point")
            if point:
                x, y = _point_to_coordinates(point, image_width, image_height)
                lines.append(f"pyautogui.mouseUp({x}, {y}, button={button!r})")
            else:
                lines.append(f"pyautogui.mouseUp(button={button!r})")
        elif action_type == "type":
            content = str(action_inputs.get("content", ""))
            stripped_content = content.rstrip("\n")
            if input_swap:
                lines.append(f"pyperclip.copy({stripped_content!r})")
                lines.append("pyautogui.hotkey('ctrl', 'v')")
            else:
                lines.append(f"pyautogui.write({stripped_content!r}, interval=0.1)")
            if content.endswith("\n"):
                lines.append("time.sleep(0.5)")
                lines.append("pyautogui.press('enter')")
        elif action_type == "finished":
            return "DONE"
        else:
            lines.append(f"# Unrecognized action type: {action_type}")

    return "\n".join(lines)


def _build_schema_map(tool_schemas: list[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    if not tool_schemas:
        return {}

    schema_map: dict[str, dict[str, Any]] = {}
    for entry in tool_schemas:
        function = entry.get("function", entry)
        name = function.get("name")
        if not name:
            continue
        schema_map[name] = {
            "required": list(function.get("parameters", {}).get("required", [])),
        }
    return schema_map


def _point_to_coordinates(point: Any, image_width: int, image_height: int) -> tuple[float, float]:
    if point is None:
        raise ValueError("Point is required for this action")

    if isinstance(point, (tuple, list)) and len(point) == 2:
        return round(float(point[0]), 3), round(float(point[1]), 3)

    raw = str(point).strip()
    match = POINT_RE.search(raw)
    if match:
        x = float(match.group(1))
        y = float(match.group(2))
    else:
        raw = raw.strip("()")
        tokens = [token for token in re.split(r"[\s,]+", raw) if token]
        if len(tokens) < 2:
            raise ValueError(f"Unsupported point format: {point}")
        x = float(tokens[0])
        y = float(tokens[1])

    if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
        x *= image_width
        y *= image_height

    return round(x, 3), round(y, 3)


def _normalize_key(key: Any) -> str:
    normalized = str(key).strip().lower()
    mapping = {
        "arrowleft": "left",
        "arrowright": "right",
        "arrowup": "up",
        "arrowdown": "down",
        "space": "space",
    }
    return mapping.get(normalized, normalized)


def _normalize_button(button: Any) -> str:
    normalized = str(button).strip().lower()
    if normalized not in {"left", "right", "middle"}:
        return "left"
    return normalized
