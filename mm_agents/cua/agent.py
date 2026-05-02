from __future__ import annotations

"""Deprecated historical CUA adapter agent.

This module belongs to the original mm_agents/cua adapter route. It is kept for
reference only and is no longer part of the supported evaluation path.
Current production path uses the blackbox bridge in osworld_cua_bridge/.
"""

import base64
import logging
import os
import re
import time
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from mm_agents.cua.translator import (
    CUAActionTranslationError,
    CUAActionTranslator,
    normalize_action_payload,
    parse_action_text,
)
from mm_agents.cua.types import (
    BRIDGE_PROTOCOL_VERSION,
    DEFAULT_ADAPTER_VERSION,
    DEFAULT_EVAL_PROFILE,
    CUAAction,
    CUAPrediction,
    CUARuntimeMetadata,
)


logger = logging.getLogger("desktopenv.agent")

if TYPE_CHECKING:
    from openai import OpenAI


def encode_image(image_content: bytes) -> str:
    return base64.b64encode(image_content).decode("utf-8")


def _preview_text(text: str, limit: int = 180) -> str:
    sanitized = text.replace("\n", "\\n")
    return sanitized if len(sanitized) <= limit else sanitized[:limit] + "..."


def _model_dump(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, list):
        return [_model_dump(item) for item in value]
    if isinstance(value, dict):
        return {key: _model_dump(item) for key, item in value.items()}
    return value


class CUAAdapterAgent:
    """Deprecated historical adapter agent.

    Keep this implementation only as archived reference. Do not use it for new
    evaluations and do not rely on it as a downgrade path.
    """

    def __init__(
        self,
        model: str = "computer-use-preview",
        max_tokens: int = 1500,
        top_p: float = 0.9,
        temperature: float = 0.0,
        action_space: str = "pyautogui",
        observation_type: str = "screenshot",
        max_trajectory_length: int = 3,
        screen_size: Tuple[int, int] = (1920, 1080),
        client_password: str = "",
        provider_name: str = "aws",
        adapter_version: str = DEFAULT_ADAPTER_VERSION,
        bridge_protocol_version: str = BRIDGE_PROTOCOL_VERSION,
        eval_profile: str = DEFAULT_EVAL_PROFILE,
        cua_version: Optional[str] = None,
        cua_repo_path: str = "",
        use_openai_responses: bool = False,
        openai_api_key_env: Optional[str] = None,
        openai_base_url_env: Optional[str] = None,
        **kwargs: Any,
    ):
        if action_space != "pyautogui":
            raise ValueError("CUAAdapterAgent only supports pyautogui action space")
        if observation_type != "screenshot":
            raise ValueError("CUAAdapterAgent currently supports screenshot observation only")

        self.model = model
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.temperature = temperature
        self.action_space = action_space
        self.observation_type = observation_type
        self.max_trajectory_length = max_trajectory_length
        self.screen_size = screen_size
        self.client_password = client_password or ("osworld-public-evaluation" if provider_name == "aws" else "password")
        self.provider_name = provider_name
        self.adapter_version = adapter_version
        self.bridge_protocol_version = bridge_protocol_version
        self.eval_profile = eval_profile
        self.cua_version = cua_version or model
        self.cua_repo_path = cua_repo_path
        self.use_openai_responses = use_openai_responses
        self.openai_api_key_env = openai_api_key_env or "OPENAI_API_KEY_CUA"
        self.openai_base_url_env = openai_base_url_env or "OPENAI_BASE_URL_CUA"
        self.extra_kwargs = kwargs

        self.translator = CUAActionTranslator()
        self.runtime_logger = logging.getLogger("desktopenv.agent")
        self._run_started_at = datetime.utcnow().isoformat()

        self.metadata = CUARuntimeMetadata(
            osworld_version=os.getenv("OSWORLD_VERSION", os.getenv("GIT_COMMIT", "unknown")),
            cua_version=self.cua_version,
            adapter_version=self.adapter_version,
            bridge_protocol_version=self.bridge_protocol_version,
            eval_profile=self.eval_profile,
            screen_size=screen_size,
            model=self.model,
            normalized_input=False,
            cua_repo_path=self.cua_repo_path,
        )

        self.observations: List[Dict[str, Any]] = []
        self.actions: List[str] = []
        self.raw_responses: List[str] = []
        self.debug_infos: List[Dict[str, Any]] = []

    def reset(self, _logger=None, **kwargs):
        self.runtime_logger = _logger if _logger is not None else logging.getLogger("desktopenv.agent")
        self.observations = []
        self.actions = []
        self.raw_responses = []
        self.debug_infos = []
        self._run_started_at = datetime.utcnow().isoformat()
        if kwargs:
            self.runtime_logger.info("CUAAdapterAgent reset with kwargs: %s", {key: value for key, value in kwargs.items() if key != "obs"})

    def _resolve_client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "openai package is required to run CUAAdapterAgent.predict()"
            ) from exc

        api_key = os.getenv(self.openai_api_key_env) or os.getenv("OPENAI_API_KEY") or os.getenv("DOUBAO_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing OpenAI-compatible API key. "
                f"Set {self.openai_api_key_env}, OPENAI_API_KEY, or DOUBAO_API_KEY."
            )

        base_url = os.getenv(self.openai_base_url_env) or os.getenv("OPENAI_BASE_URL") or os.getenv("DOUBAO_API_URL")
        if base_url:
            return OpenAI(api_key=api_key, base_url=base_url.rstrip("/"))
        return OpenAI(api_key=api_key)

    def _build_system_prompt(self) -> str:
        return (
            "You are a desktop GUI agent running inside OSWorld.\n"
            f"Platform: ubuntu\n"
            f"Password: {self.client_password}\n"
            f"Adapter version: {self.adapter_version}\n"
            f"Bridge protocol version: {self.bridge_protocol_version}\n"
            "Return exactly one JSON object or one terminal keyword per step.\n"
            "Supported terminal keywords: WAIT, DONE, FAIL.\n"
            "Supported action kinds: click, double_click, move, drag, scroll, type, hotkey, wait, done, fail.\n"
        )

    def _build_messages(self, instruction: str, obs: Dict[str, Any]) -> List[Dict[str, Any]]:
        screenshot = obs.get("screenshot")
        if not screenshot:
            raise ValueError("obs['screenshot'] is required")

        screenshot_b64 = encode_image(screenshot)
        history_lines = []
        for idx, action in enumerate(self.actions[-self.max_trajectory_length :], start=max(1, len(self.actions) - self.max_trajectory_length + 1)):
            history_lines.append(f"Step {idx}: {action}")
        history_text = "\n".join(history_lines) if history_lines else "None"

        user_text = (
            f"Task:\n{instruction}\n\n"
            f"Recent actions:\n{history_text}\n\n"
            "Return the next action as JSON with fields kind and args.\n"
            "If the task is complete, return {\"kind\":\"done\",\"args\":{...}}.\n"
            "If the task is infeasible, return {\"kind\":\"fail\",\"args\":{...}}.\n"
        )

        return [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_text},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{screenshot_b64}", "detail": "original"},
                ],
            }
        ]

    def _call_model(self, messages: List[Dict[str, Any]]) -> Any:
        client = self._resolve_client()
        request: Dict[str, Any] = {
            "model": self.model,
            "instructions": self._build_system_prompt(),
            "input": messages,
            "tools": [
                {
                    "type": "computer_use_preview",
                    "display_width": self.screen_size[0],
                    "display_height": self.screen_size[1],
                    "environment": "linux",
                }
            ],
            "truncation": "auto",
            "max_output_tokens": self.max_tokens,
        }
        if self.use_openai_responses:
            request["parallel_tool_calls"] = False
            request["reasoning"] = {"effort": "low", "summary": "concise"}
        else:
            request["reasoning"] = {"summary": "concise"}
            request["tool_choice"] = "required"
        return client.responses.create(**request)

    def _extract_action_candidates(self, response: Any) -> Tuple[List[CUAAction], str, Dict[str, Any]]:
        response_dump = _model_dump(response)
        raw_text_parts: List[str] = []
        parsed_actions: List[CUAAction] = []
        debug: Dict[str, Any] = {
            "response_id": getattr(response, "id", None) or response_dump.get("id"),
            "response_type": type(response).__name__,
            "raw_output_types": [],
        }

        output_items = getattr(response, "output", None) or response_dump.get("output", [])
        for item in output_items or []:
            item_dump = _model_dump(item)
            item_type = item_dump.get("type")
            debug["raw_output_types"].append(item_type)
            if item_type == "message":
                content = item_dump.get("content", [])
                for piece in content or []:
                    piece_text = piece.get("text") if isinstance(piece, dict) else getattr(piece, "text", "")
                    if piece_text:
                        raw_text_parts.append(str(piece_text))
                        try:
                            parsed_actions.append(parse_action_text(str(piece_text)))
                        except CUAActionTranslationError:
                            continue
            elif item_type == "computer_call":
                action_payload = item_dump.get("action", {})
                try:
                    parsed_actions.append(normalize_action_payload(action_payload))
                except CUAActionTranslationError:
                    continue
            elif item_type == "reasoning":
                summary = item_dump.get("summary", [])
                for piece in summary or []:
                    piece_text = piece.get("text") if isinstance(piece, dict) else getattr(piece, "text", "")
                    if piece_text:
                        raw_text_parts.append(str(piece_text))

        output_text = getattr(response, "output_text", None) or response_dump.get("output_text")
        if output_text:
            raw_text_parts.append(str(output_text))

        raw_text = "\n".join(text for text in raw_text_parts if text)
        return parsed_actions, raw_text, debug

    def _fallback_action(self, raw_text: str) -> CUAAction:
        if not raw_text.strip():
            return CUAAction(kind="wait", raw_text=raw_text)
        if "infeasible" in raw_text.lower():
            return CUAAction(kind="fail", raw_text=raw_text)
        if "done" in raw_text.lower():
            return CUAAction(kind="done", raw_text=raw_text)
        return CUAAction(kind="wait", raw_text=raw_text)

    def predict(self, instruction: str, obs: Dict[str, Any], **kwargs: Any) -> Tuple[str, List[str], Dict[str, Any]]:
        self.runtime_logger.info("CUAAdapterAgent predict called")
        messages = self._build_messages(instruction, obs)

        start = time.time()
        response = self._call_model(messages)
        model_duration = time.time() - start

        parsed_actions, raw_text, debug = self._extract_action_candidates(response)
        if not parsed_actions:
            parsed_actions = [self._fallback_action(raw_text)]

        actions: List[str] = []
        action_debug = []
        terminal_signal = None
        for parsed_action in parsed_actions:
            try:
                osworld_action = self.translator.to_osworld_action(parsed_action)
            except CUAActionTranslationError as exc:
                action_debug.append({"kind": parsed_action.kind, "error": str(exc)})
                osworld_action = "FAIL"
            actions.append(osworld_action)
            action_debug.append({"kind": parsed_action.kind, "args": parsed_action.args, "osworld_action": osworld_action})
            if osworld_action in {"WAIT", "DONE", "FAIL"}:
                terminal_signal = osworld_action

        response_text = raw_text or getattr(response, "output_text", "") or ""
        self.observations.append({"instruction": instruction, "obs_keys": sorted(obs.keys())})
        self.actions.append(actions[0] if actions else "WAIT")
        self.raw_responses.append(response_text)
        self.debug_infos.append({"debug": debug, "actions": action_debug})

        prediction = CUAPrediction(
            response_text=response_text,
            actions=actions,
            parsed_actions=parsed_actions,
            terminal_signal=terminal_signal,
            state_correct=terminal_signal not in {"FAIL"},
            debug={
                "model_duration": model_duration,
                "response_id": debug.get("response_id"),
                "response_type": debug.get("response_type"),
                "raw_output_types": debug.get("raw_output_types"),
                "action_debug": action_debug,
            },
        )

        info_dict = {
            "action": actions[0] if actions else "WAIT",
            "response_text": response_text,
            "terminal_signal": terminal_signal,
            "state_correct": prediction.state_correct,
            "metadata": asdict(self.metadata),
            "debug": prediction.debug,
        }
        return response_text, actions, info_dict
