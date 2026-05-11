import logging
import os
from dataclasses import dataclass

import requests

from desktop_env.providers.base import Provider

logger = logging.getLogger("desktopenv.providers.remote.RemoteProvider")
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class RemoteEndpoint:
    host: str
    server_port: int = 5000
    chromium_port: int = 9222
    vnc_port: int = 8006
    vlc_port: int = 8080

    def as_provider_address(self) -> str:
        return (
            f"{self.host}:{self.server_port}:{self.chromium_port}:"
            f"{self.vnc_port}:{self.vlc_port}"
        )


def _parse_endpoint(path_to_vm: str) -> RemoteEndpoint:
    if not path_to_vm:
        raise ValueError("Remote provider requires a non-empty endpoint.")

    parts = path_to_vm.split(":")
    if len(parts) == 1:
        return RemoteEndpoint(host=parts[0])
    if len(parts) == 2:
        return RemoteEndpoint(host=parts[0], server_port=int(parts[1]))
    if len(parts) == 5:
        return RemoteEndpoint(
            host=parts[0],
            server_port=int(parts[1]),
            chromium_port=int(parts[2]),
            vnc_port=int(parts[3]),
            vlc_port=int(parts[4]),
        )
    raise ValueError(
        "Invalid remote endpoint. Use "
        "host[:server_port[:chromium_port[:vnc_port[:vlc_port]]]]."
    )


class RemoteProvider(Provider):
    """Connect to an existing OSWorld server without managing VM lifecycle."""

    def start_emulator(self, path_to_vm: str, headless: bool, os_type: str = None, *args, **kwargs):
        endpoint = _parse_endpoint(path_to_vm)
        if os.environ.get("OSWORLD_REMOTE_SKIP_HEALTH_CHECK") == "1":
            logger.info("Skipping remote OSWorld health check.")
            return

        url = f"http://{endpoint.host}:{endpoint.server_port}/screenshot"
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                logger.info("Remote OSWorld server is reachable: %s", url)
                return
            raise RuntimeError(f"Unexpected status {response.status_code} from {url}")
        except Exception as exc:
            raise RuntimeError(
                f"Remote OSWorld server is not reachable at {url}. "
                "If it is behind SSH, create a local tunnel and pass the local endpoint."
            ) from exc

    def get_ip_address(self, path_to_vm: str) -> str:
        return _parse_endpoint(path_to_vm).as_provider_address()

    def save_state(self, path_to_vm: str, snapshot_name: str):
        logger.info("Remote provider does not save VM state.")

    def revert_to_snapshot(self, path_to_vm: str, snapshot_name: str) -> str:
        logger.info("Remote provider does not revert snapshots; reusing existing endpoint.")
        return path_to_vm

    def stop_emulator(self, path_to_vm: str, region=None, *args, **kwargs):
        logger.info("Remote provider does not stop existing machines.")

