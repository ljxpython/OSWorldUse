from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

from mm_agents.agent import PromptAgent

logger = logging.getLogger("desktopenv.agent")


class PromptAgentDemo(PromptAgent):
    """PromptAgent adapter for OpenAI-compatible custom endpoints from env vars."""

    def __init__(
        self,
        model: str | None = None,
        api_key_env: str = "DOUBAO_API_KEY",
        api_url_env: str = "DOUBAO_API_URL",
        model_env: str = "DOUBAO_API_MODEL",
        **kwargs: Any,
    ) -> None:
        resolved_model = model or os.environ.get(model_env, "").strip()
        if not resolved_model:
            raise ValueError(
                f"Model is required. Pass --model or define {model_env} in the repo .env file."
            )

        self.api_key_env = api_key_env
        self.api_url_env = api_url_env
        self.model_env = model_env
        super().__init__(model=resolved_model, **kwargs)

    def _extract_message_content(self, response_json: dict[str, Any]) -> str:
        choices = response_json.get("choices", [])
        if not choices:
            return ""

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("text"):
                    parts.append(str(item["text"]))
            return "".join(parts)

        return str(content)

    def _post_chat_completions(self, payload: dict[str, Any]) -> requests.Response:
        api_key = os.environ.get(self.api_key_env, "").strip()
        api_url = os.environ.get(self.api_url_env, "").strip()
        if not api_key:
            raise ValueError(f"Missing required env var: {self.api_key_env}")
        if not api_url:
            raise ValueError(f"Missing required env var: {self.api_url_env}")

        request_payload = dict(payload)
        request_payload["model"] = self.model
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        request_url = self._resolve_chat_completions_url(api_url)
        return requests.post(request_url, headers=headers, json=request_payload, timeout=180)

    @staticmethod
    def _resolve_chat_completions_url(api_url: str) -> str:
        normalized = api_url.rstrip("/")
        if normalized.endswith("/chat/completions"):
            return normalized

        versioned_suffixes = ("/v1", "/api/v1", "/api/v2", "/api/v3", "/compatible-mode/v1")
        if normalized.endswith(versioned_suffixes):
            return f"{normalized}/chat/completions"

        return f"{normalized}/v1/chat/completions"

    def call_llm(self, payload: dict[str, Any]) -> str:
        logger.info(
            "Generating content with custom PromptAgent demo model: %s via %s",
            self.model,
            self.api_url_env,
        )

        response = self._post_chat_completions(payload)
        if response.status_code == 200:
            return self._extract_message_content(response.json())

        try:
            error_code = response.json().get("error", {}).get("code")
        except Exception:
            error_code = None

        if error_code == "context_length_exceeded":
            logger.error("Context length exceeded. Retrying with the latest turn only.")
            retry_payload = dict(payload)
            retry_payload["messages"] = [payload["messages"][0]] + payload["messages"][-1:]
            retry_response = self._post_chat_completions(retry_payload)
            if retry_response.status_code == 200:
                return self._extract_message_content(retry_response.json())
            logger.error("Retry failed: %s", retry_response.text)
            return ""

        logger.error(
            "Failed to call custom model, status=%s, body=%s",
            response.status_code,
            response.text,
        )
        time.sleep(5)
        return ""
