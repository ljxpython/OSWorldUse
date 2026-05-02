from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from osworld_cua_bridge.executor import CuaBridgeExecutor
from osworld_cua_bridge.failures import CUA_START_FAILED, CUA_TIMEOUT, EVALUATE_FAILED, read_failure_summary, write_failure
from osworld_cua_bridge.launcher import run_cua_blackbox
from osworld_cua_bridge.protocol import BRIDGE_PROTOCOL_VERSION
from osworld_cua_bridge.reporting import build_blackbox_summary
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

    def start_recording(self) -> None:
        return None

    def end_recording(self, dest: str) -> None:
        return None


class FakeEnv:
    def __init__(self) -> None:
        self.controller = FakeController()
        self.screen_width = 1920
        self.screen_height = 1080

    def reset(self, task_config: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"screenshot": PNG_BYTES, "instruction": task_config.get("instruction") if task_config else None}

    def evaluate(self) -> float:
        return 0.0


class EvaluateFailedEnv(FakeEnv):
    def evaluate(self) -> float:
        raise RuntimeError("evaluate exploded")


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

    mapped_point_bbox = map_args_to_screen(
        "mouse_click",
        {"bbox": [500, 500]},
        screen_size=(1920, 1080),
        normalized_input=True,
    )
    assert mapped_point_bbox == {"x": 960, "y": 540}

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


def check_app_open_linux_strategy(result_dir: str) -> None:
    env, executor = _make_executor(result_dir)
    payload = _assert_ok(_request(executor, "app-open-001", "app_open", {"app": "google-chrome", "wait_ms": 0}))
    assert payload["tool"] == "app_open"
    assert "gtk-launch" in env.controller.commands[-1]
    assert "gio" in env.controller.commands[-1]
    assert "xdg-open" in env.controller.commands[-1]
    assert "shutil.which" in env.controller.commands[-1]


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


def check_launcher_failure_classification(result_dir: str) -> None:
    case_dir = os.path.join(result_dir, "launcher_start_failure")
    os.makedirs(case_dir, exist_ok=True)
    config_path = os.path.join(case_dir, "local.json")
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump({"agent": {}, "coords": {"normalizedInput": True}}, file)

    args = SimpleNamespace(
        max_steps=1,
        cua_max_duration_ms=0,
        cua_max_step_duration_ms=0,
        cua_config_path=config_path,
        cua_bin=os.path.join(case_dir, "missing-cua-binary"),
        cua_repo_root=ROOT_DIR,
        cua_runs_dir=None,
        cua_node_id="failure-smoke-node",
        screen_width=1920,
        screen_height=1080,
        cua_extra_args=None,
    )
    result = run_cua_blackbox(
        env=FakeEnv(),
        example={"id": "launcher-start-failure"},
        instruction="this should fail before CUA starts",
        args=args,
        example_result_dir=case_dir,
    )
    assert result.exit_code == 1
    assert result.failure_type == CUA_START_FAILED
    failure = read_failure_summary(case_dir)
    assert failure["primary_failure_type"] == CUA_START_FAILED
    with open(os.path.join(case_dir, "cua_meta.json"), encoding="utf-8") as file:
        meta = json.load(file)
    assert meta["failure_type"] == CUA_START_FAILED


def check_launcher_timeout_classification(result_dir: str) -> None:
    case_dir = os.path.join(result_dir, "launcher_timeout")
    os.makedirs(case_dir, exist_ok=True)
    config_path = os.path.join(case_dir, "local.json")
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump({"agent": {}, "coords": {"normalizedInput": True}}, file)

    fake_cua = os.path.join(case_dir, "fake-cua-timeout")
    with open(fake_cua, "w", encoding="utf-8") as file:
        file.write("#!/usr/bin/env bash\nsleep 10\n")
    os.chmod(fake_cua, 0o755)

    args = SimpleNamespace(
        max_steps=1,
        cua_max_duration_ms=1,
        cua_max_step_duration_ms=0,
        cua_timeout_grace_seconds=0.1,
        cua_config_path=config_path,
        cua_bin=fake_cua,
        cua_repo_root=ROOT_DIR,
        cua_runs_dir=None,
        cua_node_id="timeout-smoke-node",
        screen_width=1920,
        screen_height=1080,
        cua_extra_args=None,
    )
    result = run_cua_blackbox(
        env=FakeEnv(),
        example={"id": "launcher-timeout"},
        instruction="this should time out",
        args=args,
        example_result_dir=case_dir,
    )
    assert result.exit_code == 124
    assert result.failure_type == CUA_TIMEOUT
    failure = read_failure_summary(case_dir)
    assert failure["primary_failure_type"] == CUA_TIMEOUT


def check_evaluate_failure_classification(result_dir: str) -> None:
    from lib_run_single import run_single_example_cua_blackbox

    case_dir = os.path.join(result_dir, "evaluate_failure")
    os.makedirs(case_dir, exist_ok=True)
    config_path = os.path.join(case_dir, "local.json")
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump({"agent": {}, "coords": {"normalizedInput": True}}, file)

    fake_cua = os.path.join(case_dir, "fake-cua-success")
    with open(fake_cua, "w", encoding="utf-8") as file:
        file.write("#!/usr/bin/env bash\nexit 0\n")
    os.chmod(fake_cua, 0o755)

    args = SimpleNamespace(
        model="cua-smoke",
        adapter_version="blackbox-v1",
        bridge_protocol_version=BRIDGE_PROTOCOL_VERSION,
        eval_profile="ubuntu-cua-local-smoke-v1",
        test_all_meta_path="local-smoke",
        action_space="pyautogui",
        observation_type="screenshot",
        env_ready_sleep=0,
        settle_sleep=0,
        max_steps=1,
        cua_max_duration_ms=0,
        cua_max_step_duration_ms=0,
        cua_timeout_grace_seconds=0.1,
        cua_config_path=config_path,
        cua_bin=fake_cua,
        cua_repo_root=ROOT_DIR,
        cua_runs_dir=None,
        cua_node_id="evaluate-failure-node",
        screen_width=1920,
        screen_height=1080,
        cua_extra_args=None,
    )

    try:
        run_single_example_cua_blackbox(
            EvaluateFailedEnv(),
            {"id": "evaluate-failure", "instruction": "trigger evaluate failure"},
            1,
            "trigger evaluate failure",
            args,
            case_dir,
            [],
        )
    except RuntimeError as exc:
        assert "evaluate exploded" in str(exc)
    else:
        raise AssertionError("expected evaluate failure")

    failure = read_failure_summary(case_dir)
    assert failure["primary_failure_type"] == EVALUATE_FAILED
    with open(os.path.join(case_dir, "run_meta.json"), encoding="utf-8") as file:
        run_meta = json.load(file)
    assert run_meta["failure_type"] == EVALUATE_FAILED
    with open(os.path.join(case_dir, "cua_meta.json"), encoding="utf-8") as file:
        cua_meta = json.load(file)
    assert cua_meta["failure_type"] == EVALUATE_FAILED


def _prepare_summary_fixture(result_dir: str) -> tuple[str, dict[str, list[str]], str]:
    result_root = os.path.join(result_dir, "summary_fixture")
    task_set = {
        "browser": ["task-success", "task-timeout"],
        "office": ["task-pending"],
    }
    args_json = {
        "result_dir": result_dir,
        "action_space": "pyautogui",
        "observation_type": "screenshot",
        "model": "cua-smoke",
        "adapter_version": "blackbox-v1",
        "bridge_protocol_version": BRIDGE_PROTOCOL_VERSION,
        "eval_profile": "ubuntu-cua-local-smoke-v1",
        "cua_version": "local-smoke",
        "num_envs": 1,
        "max_steps": 1,
    }

    os.makedirs(result_root, exist_ok=True)
    with open(os.path.join(result_root, "args.json"), "w", encoding="utf-8") as file:
        json.dump(args_json, file, indent=2, ensure_ascii=False)

    meta_path = os.path.join(result_root, "test_all.json")
    with open(meta_path, "w", encoding="utf-8") as file:
        json.dump(task_set, file, indent=2, ensure_ascii=False)

    success_dir = os.path.join(result_root, "browser", "task-success")
    failed_dir = os.path.join(result_root, "browser", "task-timeout")
    os.makedirs(success_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    with open(os.path.join(success_dir, "result.txt"), "w", encoding="utf-8") as file:
        file.write("1.0\n")
    with open(os.path.join(success_dir, "runtime.log"), "w", encoding="utf-8") as file:
        file.write("ok\n")
    with open(os.path.join(success_dir, "cua_meta.json"), "w", encoding="utf-8") as file:
        json.dump({"exit_code": 0}, file, indent=2, ensure_ascii=False)

    write_failure(
        failed_dir,
        CUA_TIMEOUT,
        "synthetic timeout",
        stage="cua_process",
        details={"source": "smoke"},
    )
    with open(os.path.join(failed_dir, "runtime.log"), "w", encoding="utf-8") as file:
        file.write("timeout\n")

    return result_root, task_set, meta_path


def check_summary_totals(result_dir: str) -> None:
    result_root, task_set, meta_path = _prepare_summary_fixture(result_dir)
    summary = build_blackbox_summary(
        result_root,
        task_set=task_set,
        task_set_path=meta_path,
        metadata={
            "model": "cua-smoke",
            "adapter_version": "blackbox-v1",
            "bridge_protocol_version": BRIDGE_PROTOCOL_VERSION,
            "eval_profile": "ubuntu-cua-local-smoke-v1",
            "cua_version": "local-smoke",
        },
    )
    totals = summary["totals"]
    assert totals["total_tasks"] == 3
    assert totals["scored_tasks"] == 1
    assert totals["failed_tasks"] == 1
    assert totals["pending_tasks"] == 1
    assert totals["tasks_with_failure_metadata"] == 1
    assert totals["nonzero_score_tasks"] == 1
    assert totals["average_score"] == 1.0

    with open(os.path.join(result_root, "summary", "summary.json"), encoding="utf-8") as file:
        payload = json.load(file)
    assert payload["metadata"]["cua_version"] == "local-smoke"
    assert payload["task_set_path"] == meta_path


def check_summary_domain_and_csv(result_dir: str) -> None:
    result_root, task_set, meta_path = _prepare_summary_fixture(result_dir)
    build_blackbox_summary(result_root, task_set=task_set, task_set_path=meta_path, metadata={})

    with open(os.path.join(result_root, "summary", "domain_summary.json"), encoding="utf-8") as file:
        domains = json.load(file)
    assert domains["browser"]["total_tasks"] == 2
    assert domains["browser"]["scored_tasks"] == 1
    assert domains["browser"]["failed_tasks"] == 1
    assert domains["browser"]["average_score"] == 1.0
    assert domains["office"]["pending_tasks"] == 1

    with open(os.path.join(result_root, "summary", "summary.csv"), encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 3
    office_pending = next(row for row in rows if row["domain"] == "office" and row["task_id"] == "task-pending")
    assert office_pending["status"] == "pending"


def check_summary_rebuild_cli(result_dir: str) -> None:
    result_root, _, meta_path = _prepare_summary_fixture(result_dir)
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join(ROOT_DIR, "scripts", "python", "build_cua_blackbox_summary.py"),
            "--result_root",
            result_root,
            "--test_all_meta_path",
            meta_path,
        ],
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "summary_dir:" in proc.stdout

    with open(os.path.join(result_root, "summary", "failure_summary.json"), encoding="utf-8") as file:
        failures = json.load(file)
    timeout_bucket = failures["by_failure_type"][CUA_TIMEOUT]
    assert failures["failure_type_count"] == 1
    assert timeout_bucket["count"] == 1
    assert timeout_bucket["domains"] == ["browser"]
    assert timeout_bucket["statuses"]["failed"] == 1


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
        run_check("SMK-009", "launcher failure classification", lambda: check_launcher_failure_classification(result_dir)),
        run_check("SMK-010", "launcher timeout classification", lambda: check_launcher_timeout_classification(result_dir)),
        run_check("SMK-011", "evaluate failure classification", lambda: check_evaluate_failure_classification(result_dir)),
        run_check("SMK-012", "summary totals and metadata", lambda: check_summary_totals(result_dir)),
        run_check("SMK-013", "summary domain and csv outputs", lambda: check_summary_domain_and_csv(result_dir)),
        run_check("SMK-014", "summary rebuild cli and failure rollup", lambda: check_summary_rebuild_cli(result_dir)),
        run_check("SMK-015", "app_open linux strategy", lambda: check_app_open_linux_strategy(result_dir)),
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
