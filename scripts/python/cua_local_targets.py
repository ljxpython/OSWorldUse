from __future__ import annotations

import os


OS_TYPE_ENV_SEGMENTS = {
    "Ubuntu": "UBUNTU",
    "Windows": "WINDOWS",
    "Darwin": "DARWIN",
}


def load_repo_dotenv(root_dir: str) -> None:
    """Load repo-local .env without overriding already exported variables."""
    dotenv_path = os.path.join(root_dir, ".env")
    if not os.path.exists(dotenv_path):
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(dotenv_path, override=False)


def resolve_path_to_vm_from_env(path_to_vm: str | None, provider_name: str, os_type: str) -> str | None:
    if path_to_vm:
        return path_to_vm

    provider = provider_name.lower()
    os_segment = OS_TYPE_ENV_SEGMENTS.get(os_type, os_type.upper())
    env_names = _path_env_names(provider, os_segment)
    for env_name in env_names:
        value = os.environ.get(env_name)
        if value:
            return value
    return None


def _path_env_names(provider: str, os_segment: str) -> list[str]:
    if provider == "remote":
        return [
            f"OSWORLD_REMOTE_{os_segment}_VM",
            "OSWORLD_REMOTE_VM",
        ]
    if provider == "vmware":
        return [
            f"OSWORLD_VMWARE_{os_segment}_VMX",
            "OSWORLD_VMWARE_VMX",
            "OSWORLD_VMWARE_VM",
        ]
    return []
