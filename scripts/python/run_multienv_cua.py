from __future__ import annotations

"""Deprecated runner for the historical mm_agents/cua adapter route.

Do not use this runner for new evaluations. The supported path is
scripts/python/run_multienv_cua_blackbox.py.
"""

import argparse
import datetime
import json
import logging
import os
import signal
import sys
import time
from multiprocessing import Manager, Process, Queue, current_process
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import lib_run_single

active_environments = []
processes = []
is_terminating = False

if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Deprecated historical runner for the mm_agents/cua adapter route. "
            "Use scripts/python/run_multienv_cua_blackbox.py instead."
        )
    )

    parser.add_argument("--path_to_vm", type=str, default=None)
    parser.add_argument("--headless", action="store_true", help="Run in headless machine")
    parser.add_argument("--action_space", type=str, default="pyautogui", help="Action type")
    parser.add_argument(
        "--observation_type",
        choices=["screenshot"],
        default="screenshot",
        help="Observation type",
    )
    parser.add_argument("--sleep_after_execution", type=float, default=0.0)
    parser.add_argument("--max_steps", type=int, default=15)
    parser.add_argument("--max_trajectory_length", type=int, default=3)
    parser.add_argument("--env_ready_sleep", type=float, default=60)
    parser.add_argument("--settle_sleep", type=float, default=20)
    parser.add_argument("--test_config_base_dir", type=str, default="evaluation_examples")
    parser.add_argument("--model", type=str, default="computer-use-preview")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--max_tokens", type=int, default=1500)
    parser.add_argument("--domain", type=str, default="all")
    parser.add_argument("--example_id", type=str, default=None, help="Run a single example id within the selected domain or all domains")
    parser.add_argument("--test_all_meta_path", type=str, default="evaluation_examples/test_all.json")
    parser.add_argument("--result_dir", type=str, default="./results_cua")
    parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to run in parallel")
    parser.add_argument(
        "--log_level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument("--region", type=str, default="us-east-1")
    parser.add_argument(
        "--provider_name",
        type=str,
        default="aws",
        choices=["aws", "virtualbox", "vmware", "docker", "azure", "aliyun", "volcengine"],
    )
    parser.add_argument("--client_password", type=str, default="")
    parser.add_argument("--screen_width", type=int, default=1920)
    parser.add_argument("--screen_height", type=int, default=1080)
    parser.add_argument("--adapter_version", type=str, default="v1")
    parser.add_argument("--bridge_protocol_version", type=str, default="bridge-v1")
    parser.add_argument("--eval_profile", type=str, default="ubuntu-screenshot-pyautogui-v1")
    parser.add_argument("--cua_repo_path", type=str, default="")
    parser.add_argument("--cua_version", type=str, default=None)
    parser.add_argument("--use_openai_responses", action="store_true")
    parser.add_argument("--openai_api_key_env", type=str, default="OPENAI_API_KEY_CUA")
    parser.add_argument("--openai_base_url_env", type=str, default="OPENAI_BASE_URL_CUA")
    return parser.parse_args()


args = config()

logger = logging.getLogger()
log_level = getattr(logging, args.log_level.upper())
logger.setLevel(log_level)

os.makedirs("logs", exist_ok=True)
datetime_str = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")
file_handler = logging.FileHandler(os.path.join("logs", f"normal-{datetime_str}.log"), encoding="utf-8")
debug_handler = logging.FileHandler(os.path.join("logs", f"debug-{datetime_str}.log"), encoding="utf-8")
stdout_handler = logging.StreamHandler(sys.stdout)
file_handler.setLevel(logging.INFO)
debug_handler.setLevel(logging.DEBUG)
stdout_handler.setLevel(log_level)
formatter = logging.Formatter(
    fmt="\x1b[1;33m[%(asctime)s \x1b[31m%(levelname)s \x1b[32m%(module)s/%(lineno)d-%(processName)s\x1b[1;33m] \x1b[0m%(message)s"
)
file_handler.setFormatter(formatter)
debug_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)
stdout_handler.addFilter(logging.Filter("desktopenv"))
logger.addHandler(file_handler)
logger.addHandler(debug_handler)
logger.addHandler(stdout_handler)
logger = logging.getLogger("desktopenv.experiment")


def distribute_tasks(test_all_meta: dict) -> List[tuple]:
    all_tasks = []
    for domain, examples in test_all_meta.items():
        for example_id in examples:
            all_tasks.append((domain, example_id))
    return all_tasks


def _snapshot_name() -> str:
    if args.provider_name == "aws":
        from desktop_env.providers.aws.manager import IMAGE_ID_MAP

        screen_size = (args.screen_width, args.screen_height)
        return IMAGE_ID_MAP[args.region].get(screen_size, IMAGE_ID_MAP[args.region][(1920, 1080)])
    return "init_state"


def _build_env(screen_size):
    from desktop_env.desktop_env import DesktopEnv

    return DesktopEnv(
        path_to_vm=args.path_to_vm,
        action_space=args.action_space,
        provider_name=args.provider_name,
        region=args.region,
        snapshot_name=_snapshot_name(),
        screen_size=screen_size,
        headless=args.headless,
        os_type="Ubuntu",
        require_a11y_tree=False,
        enable_proxy=True,
        client_password=args.client_password,
    )


def run_env_tasks(task_queue: Queue, args: argparse.Namespace, shared_scores: list):
    from mm_agents.cua import CUAAdapterAgent

    active_environments = []
    env = None
    try:
        screen_size = (args.screen_width, args.screen_height)
        env = _build_env(screen_size)
        active_environments.append(env)

        agent = CUAAdapterAgent(
            model=args.model,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            temperature=args.temperature,
            action_space=args.action_space,
            observation_type=args.observation_type,
            max_trajectory_length=args.max_trajectory_length,
            screen_size=screen_size,
            client_password=args.client_password,
            provider_name=args.provider_name,
            adapter_version=args.adapter_version,
            bridge_protocol_version=args.bridge_protocol_version,
            eval_profile=args.eval_profile,
            cua_version=args.cua_version or args.model,
            cua_repo_path=args.cua_repo_path,
            use_openai_responses=args.use_openai_responses,
            openai_api_key_env=args.openai_api_key_env,
            openai_base_url_env=args.openai_base_url_env,
        )

        logger.info("Process %s started.", current_process().name)
        while True:
            try:
                domain, example_id = task_queue.get(timeout=5)
            except Exception:
                break

            try:
                config_file = os.path.join(args.test_config_base_dir, f"examples/{domain}/{example_id}.json")
                with open(config_file, "r", encoding="utf-8") as file:
                    example = json.load(file)
                logger.info("[%s][Domain]: %s", current_process().name, domain)
                logger.info("[%s][Example ID]: %s", current_process().name, example_id)
                logger.info("[%s][Instruction]: %s", current_process().name, example["instruction"])

                model_dir_name = args.model.replace("/", "__")
                example_result_dir = os.path.join(
                    args.result_dir,
                    args.action_space,
                    args.observation_type,
                    model_dir_name,
                    domain,
                    example_id,
                )
                os.makedirs(example_result_dir, exist_ok=True)
                os.makedirs(os.path.join(args.result_dir, args.action_space, args.observation_type, model_dir_name), exist_ok=True)
                with open(
                    os.path.join(args.result_dir, args.action_space, args.observation_type, model_dir_name, "args.json"),
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(vars(args), file, indent=2, ensure_ascii=False)

                try:
                    lib_run_single.run_single_example_cua(
                        agent,
                        env,
                        example,
                        args.max_steps,
                        example["instruction"],
                        args,
                        example_result_dir,
                        shared_scores,
                    )
                except Exception as exc:
                    import traceback

                    logger.error("Exception in %s %s/%s: %s", current_process().name, domain, example_id, exc)
                    logger.error(traceback.format_exc())
                    try:
                        if hasattr(env, "controller") and env.controller is not None:
                            env.controller.end_recording(os.path.join(example_result_dir, "recording.mp4"))
                    except Exception as record_exc:
                        logger.error("Failed to end recording: %s", record_exc)
                    with open(os.path.join(example_result_dir, "traj.jsonl"), "a", encoding="utf-8") as file:
                        file.write(json.dumps({"Error": f"{domain}/{example_id} - {exc}"}, ensure_ascii=False))
                        file.write("\n")
            except Exception as exc:
                import traceback

                logger.error("Task-level error in %s: %s", current_process().name, exc)
                logger.error(traceback.format_exc())
    except Exception as exc:
        import traceback

        logger.error("Process-level error in %s: %s", current_process().name, exc)
        logger.error(traceback.format_exc())
    finally:
        logger.info("%s cleaning up environment...", current_process().name)
        try:
            if env:
                env.close()
                logger.info("%s environment closed successfully", current_process().name)
        except Exception as exc:
            logger.error("%s error during environment cleanup: %s", current_process().name, exc)


def signal_handler(signum, frame):
    global is_terminating, active_environments, processes

    if is_terminating:
        return

    is_terminating = True
    logger.info("Received signal %s. Gracefully shutting down...", signum)
    for env in active_environments:
        try:
            env.close()
        except Exception as exc:
            logger.error("Error closing environment: %s", exc)
    for process in processes:
        if process.is_alive():
            try:
                process.terminate()
            except Exception as exc:
                logger.error("Error sending termination signal to process: %s", exc)
    time.sleep(1)
    for process in processes:
        if process.is_alive():
            try:
                os.kill(process.pid, signal.SIGKILL)
            except Exception as exc:
                logger.error("Error forcefully terminating process: %s", exc)
    logger.info("Shutdown complete. Exiting.")
    sys.exit(0)


def test(args: argparse.Namespace, test_all_meta: dict) -> None:
    global processes

    logger.info("Args: %s", args)
    all_tasks = distribute_tasks(test_all_meta)
    logger.info("Total tasks: %d", len(all_tasks))

    with Manager() as manager:
        shared_scores = manager.list()
        task_queue = manager.Queue()
        for item in all_tasks:
            task_queue.put(item)

        processes = []
        for index in range(args.num_envs):
            process = Process(
                target=run_env_tasks,
                args=(task_queue, args, shared_scores),
                name=f"EnvProcess-{index + 1}",
            )
            process.daemon = True
            process.start()
            processes.append(process)
            logger.info("Started process %s with PID %s", process.name, process.pid)

        try:
            while True:
                alive_count = 0
                for index, process in enumerate(processes):
                    if not process.is_alive():
                        logger.warning("Process %s died, restarting...", process.name)
                        new_process = Process(
                            target=run_env_tasks,
                            args=(task_queue, args, shared_scores),
                            name=f"EnvProcess-Restart-{index + 1}",
                        )
                        new_process.daemon = True
                        new_process.start()
                        processes[index] = new_process
                        logger.info("Restarted process %s with PID %s", new_process.name, new_process.pid)
                    else:
                        alive_count += 1

                if task_queue.empty():
                    logger.info("All tasks finished.")
                    break
                if alive_count == 0:
                    logger.error("All processes died, exiting.")
                    break
                time.sleep(5)

            for process in processes:
                process.join()
        except KeyboardInterrupt:
            logger.info("Main process received KeyboardInterrupt. Initiating graceful shutdown...")
            raise
        except Exception as exc:
            logger.error("Unexpected error while waiting for processes: %s", exc, exc_info=True)
            for process in processes:
                if process.is_alive():
                    try:
                        process.terminate()
                    except Exception as term_exc:
                        logger.error("Error terminating process %s: %s", process.name, term_exc)
            raise

        scores = list(shared_scores)

    logger.info("Average score: %s", sum(scores) / len(scores) if scores else 0)


def get_unfinished(action_space, use_model, observation_type, result_dir, total_file_json):
    target_dir = os.path.join(result_dir, action_space, observation_type, use_model)
    if not os.path.exists(target_dir):
        return total_file_json

    finished = {}
    for domain in os.listdir(target_dir):
        finished[domain] = []
        domain_path = os.path.join(target_dir, domain)
        if os.path.isdir(domain_path):
            for example_id in os.listdir(domain_path):
                if example_id == "onboard":
                    continue
                example_path = os.path.join(domain_path, example_id)
                if os.path.isdir(example_path):
                    if "result.txt" not in os.listdir(example_path):
                        for file_name in os.listdir(example_path):
                            os.remove(os.path.join(example_path, file_name))
                    else:
                        finished[domain].append(example_id)

    if not finished:
        return total_file_json

    for domain, examples in finished.items():
        if domain in total_file_json:
            total_file_json[domain] = [example_id for example_id in total_file_json[domain] if example_id not in examples]
    return total_file_json


def filter_examples(test_all_meta: dict, domain: str, example_id: str | None) -> dict:
    if domain != "all":
        test_all_meta = {domain: test_all_meta[domain]}

    if not example_id:
        return test_all_meta

    filtered = {
        domain_name: [item for item in examples if item == example_id]
        for domain_name, examples in test_all_meta.items()
    }
    filtered = {domain_name: examples for domain_name, examples in filtered.items() if examples}
    if not filtered:
        raise ValueError(f"example_id not found in selected task set: {example_id}")
    return filtered


if __name__ == "__main__":
    raise SystemExit(
        "scripts/python/run_multienv_cua.py is deprecated and no longer maintained.\n"
        "Current supported path:\n"
        "  - osworld_cua_bridge/\n"
        "  - scripts/python/run_multienv_cua_blackbox.py\n"
        "  - lib_run_single.run_single_example_cua_blackbox()\n"
        "mm_agents/cua is kept only as historical reference and must not be used as a fallback."
    )
