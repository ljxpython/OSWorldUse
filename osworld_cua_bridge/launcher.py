from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Any

from osworld_cua_bridge.executor import CuaBridgeExecutor
from osworld_cua_bridge.protocol import BRIDGE_PROTOCOL_VERSION
from osworld_cua_bridge.server import BridgeServer


DEFAULT_CUA_CONFIG_PATH = "/Users/bytedance/PycharmProjects/work/xua/runtime/agents/cua/config/local.json"
DEFAULT_CUA_REPO_ROOT = "/Users/bytedance/PycharmProjects/work/xua/runtime/agents/cua"


@dataclass
class CuaRunResult:
    run_id: str
    node_id: str
    command: list[str]
    exit_code: int
    duration_seconds: float
    stdout_path: str
    stderr_path: str
    stdout: str
    stderr: str
    bridge_url: str
    runtime_config_path: str
    config_redacted: bool


def make_run_id(example: dict[str, Any]) -> str:
    example_id = str(example.get("id") or "unknown")
    safe_example = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in example_id)
    return f"osworld-{safe_example}-{uuid.uuid4().hex[:8]}"


def resolve_cua_command(cua_bin: str | None) -> list[str]:
    if cua_bin:
        expanded = os.path.abspath(os.path.expanduser(os.path.expandvars(cua_bin)))
        if expanded.endswith(".js"):
            return ["node", expanded]
        return [expanded]

    from_path = shutil.which("cua")
    if from_path:
        return [from_path]

    candidate = "/Users/bytedance/PycharmProjects/work/xua/runtime/agents/cua/dist/cli/bin.js"
    if os.path.exists(candidate):
        return ["node", candidate]

    return ["cua"]


def run_cua_blackbox(
    env: Any,
    example: dict[str, Any],
    instruction: str,
    args: Any,
    example_result_dir: str,
) -> CuaRunResult:
    example_result_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(example_result_dir)))
    run_id = make_run_id(example)
    node_id = getattr(args, "cua_node_id", None) or f"osworld-{os.getpid()}"
    max_steps = int(getattr(args, "max_steps", 0) or 0)
    max_duration_ms = int(getattr(args, "cua_max_duration_ms", 0) or 0)
    max_step_duration_ms = int(getattr(args, "cua_max_step_duration_ms", 0) or 0)
    config_path = getattr(args, "cua_config_path", None) or DEFAULT_CUA_CONFIG_PATH
    normalized_input = _config_normalized_input(config_path)
    config_path, config_env, config_redacted = _prepare_runtime_config(config_path, example_result_dir)
    runs_dir = getattr(args, "cua_runs_dir", None) or os.path.join(example_result_dir, "cua_runs")
    runs_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(runs_dir)))
    cua_repo_root = getattr(args, "cua_repo_root", None) or DEFAULT_CUA_REPO_ROOT
    cua_repo_root = os.path.abspath(os.path.expanduser(os.path.expandvars(cua_repo_root)))
    openclaw_shim = getattr(args, "openclaw_bin", None) or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "bin",
        "openclaw",
    )

    executor = CuaBridgeExecutor(
        env=env,
        result_dir=example_result_dir,
        run_id=run_id,
        node_id=node_id,
        normalized_input=normalized_input,
    )
    server = BridgeServer(executor=executor)
    server.start()

    runtime_log_path = os.path.join(example_result_dir, "runtime.log")
    try:
        with open(runtime_log_path, "a", encoding="utf-8") as file:
            file.write(f"[osworld] bridge_url={server.url}\n")
            file.write(f"[osworld] run_id={run_id}\n")
            file.write(f"[osworld] node_id={node_id}\n")
            file.write(f"[osworld] normalized_input={normalized_input}\n")
    except Exception:
        pass

    stdout_path = os.path.join(example_result_dir, "cua.stdout.log")
    stderr_path = os.path.join(example_result_dir, "cua.stderr.log")
    os.makedirs(runs_dir, exist_ok=True)

    command = [
        *resolve_cua_command(getattr(args, "cua_bin", None)),
        "run",
        instruction,
        "--config",
        config_path,
        "--runs-dir",
        runs_dir,
        "--nodeid",
        node_id,
        "--openclaw-bin",
        openclaw_shim,
        "--target-os",
        "linux",
        "--target-screen",
        f"{int(getattr(args, 'screen_width', 1920))}x{int(getattr(args, 'screen_height', 1080))}",
        "--target-dpr",
        "1",
        "--max-steps",
        str(max_steps),
        "--no-knowledge",
        "--records-off",
        "--brain-off",
    ]
    if max_duration_ms > 0:
        command.extend(["--max-duration-ms", str(max_duration_ms)])
    if max_step_duration_ms > 0:
        command.extend(["--max-step-duration-ms", str(max_step_duration_ms)])
    if getattr(args, "cua_extra_args", None):
        command.extend(list(args.cua_extra_args))

    env_vars = os.environ.copy()
    env_vars.update(
        {
            "OSWORLD_CUA_BRIDGE_URL": server.url,
            "OSWORLD_CUA_NODE_ID": node_id,
            "OSWORLD_CUA_RUN_ID": run_id,
            "CUA_CONFIG_DIR": os.path.dirname(config_path),
        }
    )
    env_vars.update(config_env)

    start = time.time()
    try:
        with open(stdout_path, "w", encoding="utf-8") as stdout_file, open(stderr_path, "w", encoding="utf-8") as stderr_file:
            process = subprocess.run(
                command,
                stdout=stdout_file,
                stderr=stderr_file,
                text=True,
                env=env_vars,
                timeout=(max_duration_ms / 1000 + 60) if max_duration_ms > 0 else None,
                cwd=cua_repo_root,
            )
            exit_code = int(process.returncode)
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        with open(stderr_path, "a", encoding="utf-8") as stderr_file:
            stderr_file.write(f"\n[osworld] CUA process timeout: {exc}\n")
    except Exception as exc:
        exit_code = 1
        with open(stderr_path, "a", encoding="utf-8") as stderr_file:
            stderr_file.write(f"\n[osworld] CUA process failed to start: {exc}\n")
    finally:
        server.stop()
    duration = time.time() - start
    try:
        with open(runtime_log_path, "a", encoding="utf-8") as file:
            file.write(f"[osworld] cua_exit_code={exit_code}\n")
            file.write(f"[osworld] cua_duration_seconds={duration:.3f}\n")
    except Exception:
        pass
    stdout = _read_text(stdout_path)
    stderr = _read_text(stderr_path)
    result = CuaRunResult(
        run_id=run_id,
        node_id=node_id,
        command=command,
        exit_code=exit_code,
        duration_seconds=duration,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        stdout=stdout,
        stderr=stderr,
        bridge_url=server.url,
        runtime_config_path=config_path,
        config_redacted=config_redacted,
    )
    _write_meta(example_result_dir, result)
    return result


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            return file.read()
    except FileNotFoundError:
        return ""


def _write_meta(example_result_dir: str, result: CuaRunResult) -> None:
    payload = {
        "run_id": result.run_id,
        "node_id": result.node_id,
        "bridge_url": result.bridge_url,
        "command": result.command,
        "exit_code": result.exit_code,
        "duration_seconds": result.duration_seconds,
        "stdout_path": result.stdout_path,
        "stderr_path": result.stderr_path,
        "runtime_config_path": result.runtime_config_path,
        "config_redacted": result.config_redacted,
        "bridge_protocol_version": BRIDGE_PROTOCOL_VERSION,
    }
    with open(os.path.join(example_result_dir, "cua_meta.json"), "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def _prepare_runtime_config(config_path: str, example_result_dir: str) -> tuple[str, dict[str, str], bool]:
    expanded = os.path.abspath(os.path.expanduser(os.path.expandvars(config_path)))
    with open(expanded, "r", encoding="utf-8") as file:
        data = json.load(file)

    env_overrides: dict[str, str] = {}
    config_redacted = _externalize_model_api_key(data, env_overrides)

    agent = data.setdefault("agent", {})
    agent["headless"] = False
    agent["knowledge"] = {**agent.get("knowledge", {}), "enabled": False}
    agent["records"] = {**agent.get("records", {}), "enabled": False}
    agent["brain"] = {**agent.get("brain", {}), "enabled": False}
    agent["runsDir"] = os.path.abspath(os.path.join(example_result_dir, "cua_runs"))

    coords = data.setdefault("coords", {})
    coords["normalizedInput"] = bool(coords.get("normalizedInput", True))
    coords["dpr"] = 1

    runtime_config_path = os.path.abspath(os.path.join(example_result_dir, "cua_runtime_config.json"))
    with open(runtime_config_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    return runtime_config_path, env_overrides, config_redacted


def _externalize_model_api_key(data: dict[str, Any], env_overrides: dict[str, str]) -> bool:
    model = data.get("model")
    if not isinstance(model, dict):
        return False

    api_key = model.get("apiKey")
    if not isinstance(api_key, str) or not api_key:
        return False
    if "${" in api_key:
        return False

    env_name = "CUA_OSWORLD_MODEL_API_KEY"
    env_overrides[env_name] = api_key
    model["apiKey"] = f"${{{env_name}}}"
    return True


def _config_normalized_input(config_path: str) -> bool:
    expanded = os.path.abspath(os.path.expanduser(os.path.expandvars(config_path)))
    with open(expanded, "r", encoding="utf-8") as file:
        data = json.load(file)
    coords = data.get("coords", {})
    if isinstance(coords, dict):
        return bool(coords.get("normalizedInput", False))
    return False


def main() -> int:
    print("This module is intended to be imported by OSWorld runners.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
