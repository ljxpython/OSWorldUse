from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path for imports.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")

import lib_run_single
from desktop_env.desktop_env import DesktopEnv
from mm_agents.prompt_agent_demo import PromptAgentDemo


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minimal single-task benchmark runner for a PromptAgent-based custom model demo."
    )

    parser.add_argument("--path_to_vm", type=str, required=True)
    parser.add_argument("--headless", action="store_true", help="Run in headless machine")
    parser.add_argument("--provider_name", type=str, default="vmware",
                        choices=["aws", "virtualbox", "vmware", "docker", "azure", "aliyun", "volcengine"])
    parser.add_argument("--region", type=str, default="us-east-1")
    parser.add_argument("--client_password", type=str, default="")
    parser.add_argument("--screen_width", type=int, default=1920)
    parser.add_argument("--screen_height", type=int, default=1080)

    parser.add_argument("--action_space", type=str, default="pyautogui")
    parser.add_argument(
        "--observation_type",
        choices=["screenshot", "a11y_tree", "screenshot_a11y_tree", "som"],
        default="screenshot",
    )
    parser.add_argument("--sleep_after_execution", type=float, default=0.0)
    parser.add_argument("--max_steps", type=int, default=5)
    parser.add_argument("--max_trajectory_length", type=int, default=3)

    parser.add_argument("--model", type=str, default="")
    parser.add_argument("--api_key_env", type=str, default="DOUBAO_API_KEY")
    parser.add_argument("--api_url_env", type=str, default="DOUBAO_API_URL")
    parser.add_argument("--model_env", type=str, default="DOUBAO_API_MODEL")
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--max_tokens", type=int, default=1500)

    parser.add_argument(
        "--test_config_base_dir",
        type=str,
        default="evaluation_examples",
    )
    parser.add_argument(
        "--test_all_meta_path",
        type=str,
        default="docs/code-reading/examples/test_one_chrome.json",
    )
    parser.add_argument("--domain", type=str, default="")
    parser.add_argument("--example_id", type=str, default="")
    parser.add_argument("--result_dir", type=str, default="./results/prompt-agent-demo")
    parser.add_argument("--result_model_name", type=str, default="")
    parser.add_argument(
        "--log_level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
    )
    return parser.parse_args()


def setup_logging(level_name: str) -> logging.Logger:
    level = getattr(logging, level_name.upper())
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="[%(asctime)s %(levelname)s %(module)s/%(lineno)d] %(message)s"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    return logging.getLogger("desktopenv.experiment")


def resolve_task(meta_path: str, requested_domain: str, requested_example_id: str) -> tuple[str, str]:
    with open(meta_path, "r", encoding="utf-8") as f:
        test_all_meta = json.load(f)

    if not isinstance(test_all_meta, dict) or not test_all_meta:
        raise ValueError(f"Invalid or empty meta file: {meta_path}")

    domain = requested_domain or next(iter(test_all_meta.keys()))
    if domain not in test_all_meta:
        raise KeyError(f"Domain not found in meta file: {domain}")

    examples = test_all_meta[domain]
    if not examples:
        raise ValueError(f"No examples found under domain: {domain}")

    example_id = requested_example_id or examples[0]
    if example_id not in examples:
        raise KeyError(f"Example id {example_id} not found under domain {domain}")

    return domain, example_id


def main() -> None:
    args = config()
    logger = setup_logging(args.log_level)

    domain, example_id = resolve_task(args.test_all_meta_path, args.domain, args.example_id)
    config_file = os.path.join(
        args.test_config_base_dir,
        f"examples/{domain}/{example_id}.json",
    )
    with open(config_file, "r", encoding="utf-8") as f:
        example = json.load(f)

    screen_size = (args.screen_width, args.screen_height)
    env_kwargs = dict(
        path_to_vm=args.path_to_vm,
        action_space=args.action_space,
        provider_name=args.provider_name,
        screen_size=screen_size,
        headless=args.headless,
        os_type="Ubuntu",
        require_a11y_tree=args.observation_type in ["a11y_tree", "screenshot_a11y_tree", "som"],
        enable_proxy=True,
        client_password=args.client_password,
    )
    if args.provider_name == "aws":
        from desktop_env.providers.aws.manager import IMAGE_ID_MAP

        ami_id = IMAGE_ID_MAP[args.region].get(
            screen_size, IMAGE_ID_MAP[args.region][(1920, 1080)]
        )
        env_kwargs["region"] = args.region
        env_kwargs["snapshot_name"] = ami_id

    env = None
    try:
        env = DesktopEnv(**env_kwargs)
        agent = PromptAgentDemo(
            model=args.model or None,
            api_key_env=args.api_key_env,
            api_url_env=args.api_url_env,
            model_env=args.model_env,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            max_trajectory_length=args.max_trajectory_length,
            client_password=args.client_password,
        )

        model_dir_name = args.result_model_name or agent.model.replace("/", "__")
        example_result_dir = os.path.join(
            args.result_dir,
            args.action_space,
            args.observation_type,
            model_dir_name,
            domain,
            example_id,
        )
        Path(example_result_dir).mkdir(parents=True, exist_ok=True)

        args_path = os.path.join(
            args.result_dir,
            args.action_space,
            args.observation_type,
            model_dir_name,
            "args.json",
        )
        Path(args_path).parent.mkdir(parents=True, exist_ok=True)
        with open(args_path, "w", encoding="utf-8") as f:
            json.dump(vars(args), f, ensure_ascii=False, indent=2)

        logger.info("Running PromptAgent demo task: %s/%s", domain, example_id)
        logger.info("Model: %s", agent.model)
        scores: list[float] = []
        lib_run_single.run_single_example(
            agent,
            env,
            example,
            args.max_steps,
            example["instruction"],
            args,
            example_result_dir,
            scores,
        )
        logger.info("Finished. Scores: %s", scores)
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    main()
