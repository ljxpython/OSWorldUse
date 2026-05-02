from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from osworld_cua_bridge.executor import CuaBridgeExecutor
from osworld_cua_bridge.protocol import BRIDGE_PROTOCOL_VERSION
from osworld_cua_bridge.server import BridgeServer
from osworld_cua_bridge.tool_translator import map_args_to_screen, translate_tool_to_pyautogui


RUN_ID = "cua-smoke-local"
NODE_ID = "osworld-smoke-node"
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


@dataclass
class CheckResult:
    id: str
    name: str
    passed: bool
    failure_reason: str = ""


class FakeController:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def get_screenshot(self) -> bytes:
        return PNG_BYTES

    def get_vm_screen_size(self) -> dict[str, int]:
        return {"width": 1920, "height": 1080}

    def execute_python_command(self, command: str) -> dict[str, Any]:
        self.commands.append(command)
        return {"returncode": 0, "output": "ok", "error": ""}


class FakeEnv:
    def __init__(self) -> None:
        self.controller = FakeController()
        self.screen_width = 1920
        self.screen_height = 1080


def _request(executor: CuaBridgeExecutor, req_id: str, tool: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    return executor.handle_payload(
        {
            "runId": RUN_ID,
            "reqId": req_id,
            "tool": tool,
            "args": args or {},
        }
    )


def _assert_ok(response: dict[str, Any]) -> dict[str, Any]:
    assert response.get("ok") is True, response
    payload = response.get("payload")
    assert isinstance(payload, dict), response
    return payload


def _make_executor(result_dir: str) -> tuple[FakeEnv, CuaBridgeExecutor]:
    env = FakeEnv()
    executor = CuaBridgeExecutor(
        env=env,
        result_dir=result_dir,
        run_id=RUN_ID,
        node_id=NODE_ID,
        normalized_input=True,
    )
    return env, executor


def check_tool_translator() -> None:
    mapped_click = map_args_to_screen(
        "mouse_click",
        {"x": 500, "y": 500},
        screen_size=(1920, 1080),
        normalized_input=True,
    )
    assert mapped_click == {"x": 960, "y": 540}

    click = translate_tool_to_pyautogui("mouse_click", mapped_click)
    assert click == "pyautogui.moveTo(960, 540); pyautogui.click(button='left')"

    key = translate_tool_to_pyautogui("key_press", {"key": "Return"})
    assert key == "pyautogui.press('enter')"

    typed = translate_tool_to_pyautogui("clipboard_type", {"text": "abc"})
    assert "_cua_text = 'abc'" in typed

    hotkey = translate_tool_to_pyautogui("hotkey", {"keys": ["command", "l"]})
    assert hotkey == "pyautogui.hotkey('ctrl', 'l')"


def check_bridge_protocol(result_dir: str) -> None:
    _, executor = _make_executor(result_dir)
    health = executor.health()
    assert health["ok"] is True
    assert health["bridge_protocol_version"] == BRIDGE_PROTOCOL_VERSION
    assert health["runId"] == RUN_ID

    screenshot = _assert_ok(_request(executor, "ss-001", "screenshot"))
    assert screenshot["type"] == "image_base64"
    assert screenshot["imageBase64"]
    assert screenshot["width"] == 1
    assert screenshot["height"] == 1

    size = _assert_ok(_request(executor, "size-001", "get_screen_size"))
    assert '"width": 1920' in size["output"]
    assert '"height": 1080' in size["output"]

    bad = executor.handle_payload({"runId": RUN_ID, "tool": "mouse_click", "args": {}})
    assert bad["ok"] is False
    assert bad["error"]["code"] == "BAD_REQUEST"

    disabled = _request(executor, "bad-tool-001", "shell_exec", {"cmd": "pwd"})
    assert disabled["ok"] is False
    assert disabled["error"]["code"] == "UNSUPPORTED_TOOL"


def check_bridge_actions(result_dir: str) -> None:
    env, executor = _make_executor(result_dir)

    _assert_ok(_request(executor, "click-001", "mouse_click", {"x": 500, "y": 500}))
    assert "pyautogui.moveTo(960, 540)" in env.controller.commands[-1]
    command_count = len(env.controller.commands)
    _assert_ok(_request(executor, "click-001", "mouse_click", {"x": 1000, "y": 1000}))
    assert len(env.controller.commands) == command_count

    _assert_ok(_request(executor, "type-001", "clipboard_type", {"text": "hello"}))
    assert "_cua_text = 'hello'" in env.controller.commands[-1]

    _assert_ok(_request(executor, "hotkey-001", "hotkey", {"keys": ["ctrl", "l"]}))
    assert "pyautogui.hotkey('ctrl', 'l')" in env.controller.commands[-1]

    _assert_ok(_request(executor, "key-001", "key_press", {"key": "Return"}))
    assert "pyautogui.press('enter')" in env.controller.commands[-1]

    _assert_ok(_request(executor, "done-001", "done", {"reason": "smoke"}))
    assert executor.done is True
    assert executor.done_reason == "smoke"


def check_openclaw_shim(result_dir: str) -> None:
    _, executor = _make_executor(result_dir)
    server = BridgeServer(executor=executor)
    server.start()
    try:
        with urllib.request.urlopen(f"{server.url}/health", timeout=5) as response:
            health = json.loads(response.read().decode("utf-8"))
        assert health["ok"] is True

        env = os.environ.copy()
        env["OSWORLD_CUA_BRIDGE_URL"] = server.url
        env["OSWORLD_CUA_NODE_ID"] = NODE_ID
        params = json.dumps(
            {
                "runId": RUN_ID,
                "reqId": "shim-size-001",
                "tool": "get_screen_size",
                "args": {},
            }
        )
        shim = os.path.join(ROOT_DIR, "osworld_cua_bridge", "bin", "openclaw")
        proc = subprocess.run(
            [
                sys.executable,
                shim,
                "nodes",
                "invoke",
                "--node",
                NODE_ID,
                "--command",
                "cua.run",
                "--params",
                params,
            ],
            text=True,
            capture_output=True,
            timeout=10,
            env=env,
        )
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["ok"] is True
    finally:
        server.stop()


def run_check(check_id: str, name: str, fn: Callable[[], None]) -> CheckResult:
    try:
        fn()
        return CheckResult(id=check_id, name=name, passed=True)
    except Exception as exc:
        return CheckResult(id=check_id, name=name, passed=False, failure_reason=str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local smoke tests for the CUA blackbox bridge path")
    parser.add_argument("--result_dir", default="./results_cua_smoke", help="Directory for smoke artifacts")
    args = parser.parse_args()

    result_dir = os.path.abspath(args.result_dir)
    os.makedirs(result_dir, exist_ok=True)

    checks = [
        run_check("SMK-001", "module imports and blackbox translator", check_tool_translator),
        run_check("SMK-002", "bridge health and protocol errors", lambda: check_bridge_protocol(result_dir)),
        run_check("SMK-003", "bridge screenshot loop", lambda: check_bridge_protocol(result_dir)),
        run_check("SMK-004", "mouse click translation", lambda: check_bridge_actions(result_dir)),
        run_check("SMK-005", "clipboard text input translation", lambda: check_bridge_actions(result_dir)),
        run_check("SMK-006", "hotkey and key press translation", lambda: check_bridge_actions(result_dir)),
        run_check("SMK-007", "done terminal semantics", lambda: check_bridge_actions(result_dir)),
        run_check("SMK-008", "openclaw shim and structured errors", lambda: check_openclaw_shim(result_dir)),
    ]

    passed = all(item.passed for item in checks)
    report = {
        "run_id": RUN_ID,
        "cua_version": "local-smoke",
        "adapter_version": "blackbox-v1",
        "bridge_protocol_version": BRIDGE_PROTOCOL_VERSION,
        "eval_profile": "ubuntu-cua-local-smoke-v1",
        "task_id": "local-bridge-smoke",
        "result": "pass" if passed else "fail",
        "failure_reason": "; ".join(item.failure_reason for item in checks if not item.passed),
        "artifact_paths": [result_dir],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "checks": [item.__dict__ for item in checks],
    }
    report_path = os.path.join(result_dir, "cua_smoke_report.json")
    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    for item in checks:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status} {item.id} {item.name}")
        if item.failure_reason:
            print(f"  {item.failure_reason}")
    print(f"report: {report_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
