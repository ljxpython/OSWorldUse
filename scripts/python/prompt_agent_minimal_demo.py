from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports, same pattern as other runnable scripts.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from mm_agents.agent import PromptAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minimal PromptAgent demo for learning prompt construction and action parsing."
    )
    parser.add_argument("--image", type=str, required=True, help="Path to a PNG/JPG screenshot file.")
    parser.add_argument(
        "--instruction",
        type=str,
        default="Please open the browser and search for OSWorld benchmark.",
        help="Task instruction passed to PromptAgent.predict().",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="Model name when running in live mode. Ignored in mock mode.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually call the configured model API instead of returning a mock response.",
    )
    parser.add_argument(
        "--dump-messages",
        type=str,
        default="",
        help="Optional path to save the sanitized LLM payload JSON for inspection.",
    )
    return parser.parse_args()


def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = {
        "model": payload["model"],
        "max_tokens": payload["max_tokens"],
        "top_p": payload["top_p"],
        "temperature": payload["temperature"],
        "messages": [],
    }

    for message in payload["messages"]:
        sanitized_message = {"role": message["role"], "content": []}
        for part in message["content"]:
            if part["type"] == "image_url":
                url = part["image_url"]["url"]
                sanitized_message["content"].append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"[base64 image omitted, {len(url)} chars]",
                            "detail": part["image_url"].get("detail", ""),
                        },
                    }
                )
            else:
                sanitized_message["content"].append(part)
        sanitized["messages"].append(sanitized_message)

    return sanitized


def default_mock_response() -> str:
    return """```python
pyautogui.click(320, 240)
pyautogui.write("OSWorld benchmark")
pyautogui.press("enter")
```"""


def main() -> None:
    args = parse_args()
    image_path = Path(args.image).expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    agent = PromptAgent(
        model=args.model,
        observation_type="screenshot",
        action_space="pyautogui",
        max_trajectory_length=1,
    )
    agent.reset()

    obs = {
        "screenshot": image_path.read_bytes(),
        "accessibility_tree": None,
        "terminal": None,
        "instruction": args.instruction,
    }

    if not args.live:
        def mock_call_llm(payload: dict[str, Any]) -> str:
            sanitized = sanitize_payload(payload)
            if args.dump_messages:
                dump_path = Path(args.dump_messages).expanduser().resolve()
                dump_path.parent.mkdir(parents=True, exist_ok=True)
                dump_path.write_text(json.dumps(sanitized, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                print("=== Sanitized payload preview ===")
                print(json.dumps(sanitized, ensure_ascii=False, indent=2))
            return default_mock_response()

        agent.call_llm = mock_call_llm  # type: ignore[method-assign]

    response, actions = agent.predict(args.instruction, obs)

    print("\n=== Raw model response ===")
    print(response)
    print("\n=== Parsed actions ===")
    print(json.dumps(actions, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
