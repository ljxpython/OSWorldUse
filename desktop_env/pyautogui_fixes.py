from __future__ import annotations

import ast
import re


def fix_pyautogui_less_than_bug(command: str) -> str:
    """
    Fix PyAutoGUI '<' character bug by converting it to hotkey("shift", ',') calls.

    This fixes the known PyAutoGUI issue where typing '<' produces '>' instead.
    References:
    - https://github.com/asweigart/pyautogui/issues/198
    - https://github.com/xlang-ai/OSWorld/issues/257
    """
    press_pattern = r'pyautogui\.press\(["\'](?:<|\\u003c)["\']\)'

    def replace_press_less_than(match):
        return 'pyautogui.hotkey("shift", ",")'

    command = re.sub(press_pattern, replace_press_less_than, command)

    # Rewrite pyautogui.write/typewrite calls using Python's parser instead of
    # regex string matching. The command may contain shell fragments such as
    # `sed 's/$/<br\\/>/'`; regex sees the inner quotes and can split the Python
    # literal incorrectly, producing invalid controller code.
    def expand_typewrite_text(text: str) -> list[str]:
        parts = text.split("<")
        out: list[str] = []
        for i, part in enumerate(parts):
            if i == 0:
                if part:
                    out.append(f"pyautogui.typewrite({part!r})")
            else:
                out.append('pyautogui.hotkey("shift", ",")')
                if part:
                    out.append(f"pyautogui.typewrite({part!r})")
        return out

    try:
        module = ast.parse(command)
        rewritten: list[str] = []
        changed = False
        for stmt in module.body:
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr in {"typewrite", "write"}
                and isinstance(stmt.value.func.value, ast.Name)
                and stmt.value.func.value.id == "pyautogui"
                and stmt.value.args
                and isinstance(stmt.value.args[0], ast.Constant)
                and isinstance(stmt.value.args[0].value, str)
                and "<" in stmt.value.args[0].value
            ):
                rewritten.extend(expand_typewrite_text(stmt.value.args[0].value))
                changed = True
            else:
                rewritten.append(ast.unparse(stmt))
        if changed:
            command = "; ".join(rewritten)
    except SyntaxError:
        typewrite_pattern = r'pyautogui\.(?:typewrite|write)\((["\'])(.*?)\1\)'

        def process_typewrite_match(match):
            quote_char = match.group(1)
            content = match.group(2)
            try:
                content = content.encode("utf-8").decode("unicode_escape")
            except UnicodeDecodeError:
                pass
            if "<" not in content:
                return match.group(0)
            result_parts = []
            for i, part in enumerate(content.split("<")):
                if i == 0:
                    if part:
                        result_parts.append(
                            f"pyautogui.typewrite({quote_char}{part}{quote_char})"
                        )
                else:
                    result_parts.append('pyautogui.hotkey("shift", ",")')
                    if part:
                        result_parts.append(
                            f"pyautogui.typewrite({quote_char}{part}{quote_char})"
                        )
            return "; ".join(result_parts)

        command = re.sub(typewrite_pattern, process_typewrite_match, command)

    return command
