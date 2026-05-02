from __future__ import annotations

import base64
import json
import logging
import os
import threading
import time
from typing import Any

from osworld_cua_bridge.failures import bridge_failure_type_from_code
from osworld_cua_bridge.protocol import BRIDGE_PROTOCOL_VERSION, BridgeProtocolError, BridgeRequest, error, ok, parse_request
from osworld_cua_bridge.tool_translator import ToolTranslationError, map_args_to_screen, tool_output, translate_tool_to_pyautogui


logger = logging.getLogger("desktopenv.cua_bridge")


def _read_image_metadata(image: bytes) -> tuple[int | None, int | None, str]:
    if len(image) >= 24 and image[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(image[16:20], "big"), int.from_bytes(image[20:24], "big"), "image/png"

    if len(image) >= 4 and image[0] == 0xFF and image[1] == 0xD8:
        idx = 2
        while idx + 4 < len(image):
            if image[idx] != 0xFF:
                idx += 1
                continue
            while idx < len(image) and image[idx] == 0xFF:
                idx += 1
            if idx >= len(image):
                break
            marker = image[idx]
            idx += 1
            if marker in {0xD9, 0xDA} or idx + 1 >= len(image):
                break
            segment_length = int.from_bytes(image[idx:idx + 2], "big")
            if segment_length < 2 or idx + segment_length > len(image):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                if idx + 7 < len(image):
                    height = int.from_bytes(image[idx + 3:idx + 5], "big")
                    width = int.from_bytes(image[idx + 5:idx + 7], "big")
                    return width, height, "image/jpeg"
                break
            idx += segment_length
        return None, None, "image/jpeg"

    return None, None, "application/octet-stream"


class CuaBridgeExecutor:
    def __init__(self, env: Any, result_dir: str, run_id: str, node_id: str, normalized_input: bool):
        self.env = env
        self.result_dir = result_dir
        self.run_id = run_id
        self.node_id = node_id
        self.normalized_input = normalized_input
        self.done = False
        self.done_reason: str | None = None
        self._lock = threading.RLock()
        self._request_count = 0
        self._cache: dict[str, dict[str, Any]] = {}
        self._log_path = os.path.join(result_dir, "bridge_requests.jsonl")
        self._screenshot_dir = os.path.join(result_dir, "bridge_screenshots")
        self._screen_size: tuple[int, int] | None = None
        self._failure_counts: dict[str, int] = {}
        self._last_failure: dict[str, Any] | None = None
        os.makedirs(self._screenshot_dir, exist_ok=True)

    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "bridge_protocol_version": BRIDGE_PROTOCOL_VERSION,
            "runId": self.run_id,
            "nodeId": self.node_id,
            "done": self.done,
            "requestCount": self._request_count,
        }

    def handle_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            req = parse_request(payload)
            if req.run_id != self.run_id:
                response = error(
                    "BAD_REQUEST",
                    f"runId mismatch: expected {self.run_id}, got {req.run_id}",
                    {"expectedRunId": self.run_id, "actualRunId": req.run_id},
                )
                self._record_response_failure(req.tool, response)
                self._write_log(req, response, cached=False)
                return response
            cached = self._cache.get(req.req_id)
            if cached:
                self._write_log(req, cached, cached=True)
                return cached

            with self._lock:
                self._request_count += 1
                if req.tool == "screenshot":
                    response = self._screenshot(req)
                elif req.tool == "get_screen_size":
                    response = self._get_screen_size(req)
                elif req.tool == "done":
                    response = self._done(req)
                else:
                    response = self._execute_gui_tool(req)

            self._cache[req.req_id] = response
            self._record_response_failure(req.tool, response)
            self._write_log(req, response, cached=False)
            return response
        except BridgeProtocolError as exc:
            response = error(exc.code, exc.message, exc.details)
            self._record_raw_response_failure(payload, response)
            self._write_raw_log(payload, response)
            return response
        except Exception as exc:
            logger.exception("CUA bridge request failed")
            response = error("EXEC_FAILED", str(exc))
            self._record_raw_response_failure(payload, response)
            self._write_raw_log(payload, response)
            return response

    def _screenshot(self, req: BridgeRequest) -> dict[str, Any]:
        screenshot = self.env.controller.get_screenshot()
        if not screenshot:
            return error("SCREENSHOT_FAILED", "screenshot returned empty payload", {"reqId": req.req_id})

        width, height, mime = _read_image_metadata(screenshot)

        image_path = os.path.join(self._screenshot_dir, f"{self._safe_file_part(req.req_id)}.png")
        try:
            with open(image_path, "wb") as file:
                file.write(screenshot)
        except Exception:
            logger.exception("failed to save bridge screenshot")

        payload = {
            "type": "image_base64",
            "mime": mime,
            "width": width,
            "height": height,
            "imageBase64": base64.b64encode(screenshot).decode("ascii"),
            "output": image_path,
            "runId": req.run_id,
            "reqId": req.req_id,
        }
        return ok(payload)

    def _get_screen_size(self, req: BridgeRequest) -> dict[str, Any]:
        screen_size = None
        try:
            screen_size = self.env.controller.get_vm_screen_size()
        except Exception:
            logger.exception("failed to get VM screen size from controller")

        width = None
        height = None
        if isinstance(screen_size, dict):
            width = screen_size.get("width")
            height = screen_size.get("height")
        width = int(width or getattr(self.env, "screen_width", 0) or 0)
        height = int(height or getattr(self.env, "screen_height", 0) or 0)
        if width <= 0 or height <= 0:
            return error("SCREEN_SIZE_FAILED", "invalid screen size", {"screenSize": screen_size})
        return ok(
            {
                "type": "tool_result",
                "tool": req.tool,
                "runId": req.run_id,
                "reqId": req.req_id,
                "output": json.dumps({"width": width, "height": height, "os": "linux", "dpr": 1}, ensure_ascii=False),
            }
        )

    def _done(self, req: BridgeRequest) -> dict[str, Any]:
        self.done = True
        self.done_reason = str(req.args.get("reason") or "")
        return ok(
            {
                "type": "tool_result",
                "tool": req.tool,
                "runId": req.run_id,
                "reqId": req.req_id,
                "output": f"done: {self.done_reason}",
            }
        )

    def _execute_gui_tool(self, req: BridgeRequest) -> dict[str, Any]:
        try:
            if self._screen_size is None:
                self._screen_size = self._resolve_screen_size()
            mapped_args = map_args_to_screen(
                req.tool,
                req.args,
                screen_size=self._screen_size,
                normalized_input=self.normalized_input,
            )
            if req.tool == "clipboard_type":
                command = self._clipboard_command(req.args)
            elif req.tool == "app_open":
                command = self._app_open_command(req.args)
            else:
                command = translate_tool_to_pyautogui(req.tool, mapped_args)
        except ToolTranslationError as exc:
            return error("TOOL_TRANSLATION_FAILED", str(exc), {"tool": req.tool, "args": req.args})

        if not command:
            return error("UNSUPPORTED_TOOL", f"unsupported tool: {req.tool}", {"tool": req.tool})

        result = self.env.controller.execute_python_command(command)
        if result is None:
            return error("CONTROLLER_EXEC_FAILED", "controller returned empty result", {"tool": req.tool, "command": command})
        if isinstance(result, dict):
            returncode = result.get("returncode", 0)
            status = result.get("status")
            if returncode not in (0, None) or status == "error":
                return error(
                    "CONTROLLER_EXEC_FAILED",
                    str(result.get("error") or result.get("message") or "command failed"),
                    {"result": result, "command": command},
                )

        return ok(
            {
                "type": "tool_result",
                "tool": req.tool,
                "runId": req.run_id,
                "reqId": req.req_id,
                "output": tool_output(req.tool, req.args),
                "mappedArgs": mapped_args,
                "command": command,
                "controllerResult": result,
            }
        )

    def failure_summary(self) -> dict[str, Any]:
        return {
            "bridge_error_count": sum(self._failure_counts.values()),
            "bridge_failure_counts": dict(sorted(self._failure_counts.items())),
            "bridge_failure_types": sorted(self._failure_counts),
            "last_bridge_failure": self._last_failure,
        }

    def _record_response_failure(self, tool: str, response: dict[str, Any]) -> None:
        if response.get("ok") is True:
            return
        error_payload = response.get("error")
        if not isinstance(error_payload, dict):
            failure_type = "bridge_exec_failed"
            message = json.dumps(response, ensure_ascii=False, default=str)
            code = "UNKNOWN"
            details = {}
        else:
            code = str(error_payload.get("code") or "UNKNOWN")
            failure_type = bridge_failure_type_from_code(code)
            message = str(error_payload.get("message") or "")
            details = error_payload.get("details") if isinstance(error_payload.get("details"), dict) else {}

        self._failure_counts[failure_type] = self._failure_counts.get(failure_type, 0) + 1
        self._last_failure = {
            "failure_type": failure_type,
            "failure_reason": message,
            "bridge_error_code": code,
            "tool": tool,
            "details": details,
            "timestamp": time.time(),
        }

    def _record_raw_response_failure(self, payload: dict[str, Any], response: dict[str, Any]) -> None:
        tool = str(payload.get("tool") or "")
        self._record_response_failure(tool, response)

    def _write_log(self, req: BridgeRequest, response: dict[str, Any], cached: bool) -> None:
        record = {
            "timestamp": time.time(),
            "cached": cached,
            "request": {
                "runId": req.run_id,
                "reqId": req.req_id,
                "tool": req.tool,
                "args": req.args,
            },
            "response": self._truncate_response(response),
        }
        self._append_log(record)

    def _write_raw_log(self, payload: dict[str, Any], response: dict[str, Any]) -> None:
        record = {
            "timestamp": time.time(),
            "cached": False,
            "request": payload,
            "response": self._truncate_response(response),
        }
        self._append_log(record)

    def _append_log(self, record: dict[str, Any]) -> None:
        try:
            with open(self._log_path, "a", encoding="utf-8") as file:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            logger.exception("failed to append CUA bridge request log")

    @staticmethod
    def _truncate_response(response: dict[str, Any]) -> dict[str, Any]:
        copied = json.loads(json.dumps(response, ensure_ascii=False, default=str))
        payload = copied.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("imageBase64"), str):
            payload["imageBase64"] = f"<base64:{len(payload['imageBase64'])}>"
        return copied

    @staticmethod
    def _safe_file_part(value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in value)[:180]

    def _resolve_screen_size(self) -> tuple[int, int] | None:
        screen_size = None
        try:
            screen_size = self.env.controller.get_vm_screen_size()
        except Exception:
            logger.exception("failed to get VM screen size from controller")

        width = None
        height = None
        if isinstance(screen_size, dict):
            width = screen_size.get("width")
            height = screen_size.get("height")
        width = int(width or getattr(self.env, "screen_width", 0) or 0)
        height = int(height or getattr(self.env, "screen_height", 0) or 0)
        if width > 0 and height > 0:
            return width, height
        return None

    @staticmethod
    def _clipboard_command(args: dict[str, Any]) -> str:
        text = str(args.get("text") or "")
        if not text:
            raise ToolTranslationError("text must not be empty")
        text_repr = repr(text)
        return (
            f"_cua_text = {text_repr}; "
            "\ntry:\n"
            "    import pyperclip\n"
            "    pyperclip.copy(_cua_text)\n"
            "    pyautogui.hotkey('ctrl', 'v')\n"
            "except Exception:\n"
            "    try:\n"
            "        import subprocess, shlex\n"
            "        subprocess.run(['bash', '-lc', f\"printf %s {_cua_text!r} | xclip -selection clipboard\"], check=True)\n"
            "        pyautogui.hotkey('ctrl', 'v')\n"
            "    except Exception:\n"
            "        pyautogui.write(_cua_text)\n"
        )

    @staticmethod
    def _app_open_command(args: dict[str, Any]) -> str:
        app = str(args.get("app") or args.get("bundle_id") or "").strip()
        if not app:
            raise ToolTranslationError("app_open needs app or bundle_id")
        try:
            wait_ms = max(0, int(float(args.get("wait_ms", 1500) or 0)))
        except (TypeError, ValueError) as exc:
            raise ToolTranslationError("wait_ms must be a number") from exc
        app_repr = repr(app)
        wait_seconds = wait_ms / 1000.0
        return (
            "import json, os, shutil, subprocess, time\n"
            f"_cua_app = {app_repr}\n"
            f"_cua_wait_seconds = {wait_seconds!r}\n"
            "_cua_errors = []\n"
            "_cua_search_paths = [\n"
            "    '/usr/share/applications',\n"
            "    '/usr/local/share/applications',\n"
            "    os.path.expanduser('~/.local/share/applications'),\n"
            "    os.path.expanduser('~/.local/share/flatpak/exports/share/applications'),\n"
            "    '/var/lib/flatpak/exports/share/applications',\n"
            "]\n"
            "\n"
            "def _cua_sleep():\n"
            "    if _cua_wait_seconds > 0:\n"
            "        time.sleep(_cua_wait_seconds)\n"
            "\n"
            "def _cua_success(strategy, **extra):\n"
            "    _cua_sleep()\n"
            "    payload = {'event': 'app_open', 'os': 'linux', 'strategy': strategy, **extra}\n"
            "    print(json.dumps(payload, ensure_ascii=False))\n"
            "\n"
            "def _cua_find_desktop_file(name):\n"
            "    candidates = [name]\n"
            "    if not name.endswith('.desktop'):\n"
            "        candidates.append(f'{name}.desktop')\n"
            "    lowered = name.lower()\n"
            "    for directory in _cua_search_paths:\n"
            "        if not os.path.isdir(directory):\n"
            "            continue\n"
            "        for candidate in candidates:\n"
            "            path = os.path.join(directory, candidate)\n"
            "            if os.path.exists(path):\n"
            "                return path\n"
            "        try:\n"
            "            for filename in os.listdir(directory):\n"
            "                if not filename.endswith('.desktop'):\n"
            "                    continue\n"
            "                path = os.path.join(directory, filename)\n"
            "                try:\n"
            "                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:\n"
            "                        content = file.read().lower()\n"
            "                except OSError:\n"
            "                    continue\n"
            "                if lowered in filename.lower() or f'name={lowered}' in content:\n"
            "                    return path\n"
            "        except OSError:\n"
            "            continue\n"
            "    return None\n"
            "\n"
            "try:\n"
            "    result = subprocess.run(['gtk-launch', _cua_app], text=True, capture_output=True, timeout=5)\n"
            "    if result.returncode == 0:\n"
            "        _cua_success('gtk-launch', app=_cua_app)\n"
            "        raise SystemExit(0)\n"
            "    _cua_errors.append(f\"gtk-launch: {(result.stderr or result.stdout or 'failed')[:200]}\")\n"
            "except Exception as exc:\n"
            "    _cua_errors.append(f'gtk-launch: {str(exc)[:100]}')\n"
            "\n"
            "try:\n"
            "    desktop_file = _cua_find_desktop_file(_cua_app)\n"
            "    if desktop_file:\n"
            "        result = subprocess.run(['gio', 'launch', desktop_file], text=True, capture_output=True, timeout=5)\n"
            "        if result.returncode == 0:\n"
            "            _cua_success('gio-launch', desktop_file=desktop_file)\n"
            "            raise SystemExit(0)\n"
            "        _cua_errors.append(f\"gio launch: {(result.stderr or result.stdout or 'failed')[:200]}\")\n"
            "except Exception as exc:\n"
            "    _cua_errors.append(f'gio: {str(exc)[:100]}')\n"
            "\n"
            "try:\n"
            "    result = subprocess.run(['xdg-open', _cua_app], text=True, capture_output=True, timeout=6)\n"
            "    if result.returncode == 0:\n"
            "        _cua_success('xdg-open', app=_cua_app)\n"
            "        raise SystemExit(0)\n"
            "    _cua_errors.append(f\"xdg-open: {(result.stderr or result.stdout or 'failed')[:200]}\")\n"
            "except Exception as exc:\n"
            "    _cua_errors.append(f'xdg-open: {str(exc)[:100]}')\n"
            "\n"
            "try:\n"
            "    executable = shutil.which(_cua_app)\n"
            "    if executable:\n"
            "        subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)\n"
            "        _cua_success('exec', app=_cua_app, executable=executable)\n"
            "        raise SystemExit(0)\n"
            "except Exception as exc:\n"
            "    _cua_errors.append(f'exec: {str(exc)[:100]}')\n"
            "\n"
            "raise RuntimeError('Linux app_open failed: ' + ' | '.join(_cua_errors))\n"
        )
