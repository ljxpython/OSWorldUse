import logging
import os
import platform
import re
import shutil
import subprocess
import time
import ipaddress

from desktop_env.providers.base import Provider

logger = logging.getLogger("desktopenv.providers.vmware.VMwareProvider")
logger.setLevel(logging.INFO)

WAIT_TIME = 3
VMCLI_QUERY_TIMEOUT = 15
MAX_IP_DISCOVERY_FAILURES_BEFORE_RESTART = 2


def get_vmrun_type(return_list=False):
    if platform.system() == 'Windows' or platform.system() == 'Linux':
        if return_list:
            return ['-T', 'ws']
        else:
            return '-T ws'
    elif platform.system() == 'Darwin':  # Darwin is the system name for macOS
        if return_list:
            return ['-T', 'fusion']
        else:
            return '-T fusion'
    else:
        raise Exception("Unsupported operating system")


class VMwareProvider(Provider):
    def __init__(self, region: str = None):
        super().__init__(region)
        self._headless = False
        self._os_type = "Ubuntu"
        self._was_running_before_start = False

    @staticmethod
    def _execute_command(command: list, return_output=False):
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        stdout, stderr = process.communicate()

        if return_output:
            return stdout.strip()
        else:
            if process.returncode != 0:
                logger.warning(
                    "Command failed, returncode=%s, command=%s, stderr=%s",
                    process.returncode,
                    " ".join(command),
                    (stderr or "").strip() or "<empty>",
                )
                # vmrun sometimes prints errors to stdout; surface it for debugging.
                if (stdout or "").strip():
                    logger.warning("Command stdout: %s", stdout.strip())
            return None

    @staticmethod
    def _validate_ip(value: str) -> str | None:
        if not value:
            return None

        try:
            ipaddress.ip_address(value)
        except ValueError:
            return None
        return value

    @staticmethod
    def _get_vmcli_path() -> str | None:
        if platform.system() != "Darwin":
            return None

        vmcli_path = shutil.which("vmcli")
        if vmcli_path:
            return vmcli_path

        fallback_path = "/Applications/VMware Fusion.app/Contents/Library/vmcli"
        if os.path.exists(fallback_path):
            return fallback_path
        return None

    def _query_vmcli_guest_state(self, path_to_vm: str) -> tuple[str | None, bool | None]:
        vmcli_path = self._get_vmcli_path()
        if not vmcli_path:
            return None, None

        try:
            result = subprocess.run(
                [vmcli_path, path_to_vm, "Guest", "query"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                timeout=VMCLI_QUERY_TIMEOUT,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            logger.warning("Failed to query vmcli guest state: %s", exc)
            return None, None

        if result.returncode != 0:
            logger.warning(
                "vmcli Guest query failed, returncode=%s, stderr=%s",
                result.returncode,
                (result.stderr or "").strip() or "<empty>",
            )
            if (result.stdout or "").strip():
                logger.warning("vmcli Guest query stdout: %s", result.stdout.strip())
            return None, None

        ip_match = re.search(r"^ip:\s*'([^']*)'", result.stdout, re.MULTILINE)
        running_match = re.search(r"^vmIsRunning:\s*(true|false)", result.stdout, re.MULTILINE)

        vmcli_ip = self._validate_ip((ip_match.group(1) if ip_match else "").strip())
        vm_is_running = None if not running_match else running_match.group(1) == "true"
        return vmcli_ip, vm_is_running

    def _restart_vm_for_network_recovery(self, path_to_vm: str):
        logger.warning("Restarting VMware VM once to recover guest networking.")
        VMwareProvider._execute_command(
            ["vmrun"] + get_vmrun_type(return_list=True) + ["stop", path_to_vm, "hard"]
        )
        time.sleep(WAIT_TIME)
        self._was_running_before_start = False
        self.start_emulator(path_to_vm, self._headless, self._os_type)

    def start_emulator(self, path_to_vm: str, headless: bool, os_type: str):
        print("Starting VMware VM...")
        logger.info("Starting VMware VM...")
        self._headless = headless
        self._os_type = os_type

        normalized_path_to_vm = os.path.abspath(os.path.normpath(path_to_vm))
        if not os.path.exists(normalized_path_to_vm):
            raise FileNotFoundError(
                f"VMX not found: {normalized_path_to_vm}. "
                "If you manually deleted vmware_vm_data, remove stale entries in .vmware_vms or rerun to re-install the VM."
            )

        self._was_running_before_start = False
        started_in_this_call = False
        while True:
            try:
                output = subprocess.check_output(f"vmrun {get_vmrun_type()} list", shell=True, stderr=subprocess.STDOUT)
                output = output.decode()
                output = output.splitlines()

                if any(os.path.abspath(os.path.normpath(line)) == normalized_path_to_vm for line in output):
                    self._was_running_before_start = not started_in_this_call
                    logger.info("VM is running.")
                    break
                else:
                    logger.info("Starting VM...")
                    _command = ["vmrun"] + get_vmrun_type(return_list=True) + ["start", normalized_path_to_vm]
                    if headless:
                        _command.append("nogui")
                    VMwareProvider._execute_command(_command)
                    started_in_this_call = True
                    time.sleep(WAIT_TIME)

            except subprocess.CalledProcessError as e:
                logger.error(f"Error executing command: {e.output.decode().strip()}")

    def get_ip_address(self, path_to_vm: str) -> str:
        logger.info("Getting VMware VM IP address...")
        normalized_path_to_vm = os.path.abspath(os.path.normpath(path_to_vm))
        consecutive_failures = 0
        recovery_attempted = False
        while True:
            try:
                result = subprocess.run(
                    ["vmrun"] + get_vmrun_type(return_list=True) + ["getGuestIPAddress", normalized_path_to_vm, "-wait"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                )
                output = result.stdout.strip()
                error = result.stderr.strip()

                vmcli_ip, vm_is_running = self._query_vmcli_guest_state(normalized_path_to_vm)

                if result.returncode == 0:
                    validated_ip = self._validate_ip(output)
                    if validated_ip:
                        logger.info(f"VMware VM IP address: {validated_ip}")
                        return validated_ip

                    if output and output.lower() != "unknown":
                        logger.warning("VMware VM returned invalid IP address: %s", output)
                else:
                    logger.warning(
                        "Failed to get VMware VM IP address, returncode=%s, stderr=%s, stdout=%s",
                        result.returncode,
                        error or "<empty>",
                        output or "<empty>",
                    )

                if vmcli_ip:
                    logger.info("VMware VM IP address from vmcli Guest query: %s", vmcli_ip)
                    return vmcli_ip

                consecutive_failures += 1
                if output.lower() == "unknown" or not output:
                    logger.info("VMware VM IP address is not ready yet: %s", output or "<empty>")

                should_restart = (
                    not recovery_attempted
                    and vm_is_running is not False
                    and (
                        self._was_running_before_start
                        or consecutive_failures >= MAX_IP_DISCOVERY_FAILURES_BEFORE_RESTART
                    )
                )
                if should_restart:
                    self._restart_vm_for_network_recovery(normalized_path_to_vm)
                    recovery_attempted = True
                    consecutive_failures = 0
                    continue

                time.sleep(WAIT_TIME)
            except Exception as e:
                logger.error(e)
                time.sleep(WAIT_TIME)
                logger.info("Retrying to get VMware VM IP address...")

    def save_state(self, path_to_vm: str, snapshot_name: str):
        logger.info("Saving VMware VM state...")
        VMwareProvider._execute_command(
            ["vmrun"] + get_vmrun_type(return_list=True) + ["snapshot", path_to_vm, snapshot_name])
        time.sleep(WAIT_TIME)  # Wait for the VM to save

    def revert_to_snapshot(self, path_to_vm: str, snapshot_name: str):
        logger.info(f"Reverting VMware VM to snapshot: {snapshot_name}...")
        VMwareProvider._execute_command(
            ["vmrun"] + get_vmrun_type(return_list=True) + ["revertToSnapshot", path_to_vm, snapshot_name])
        time.sleep(WAIT_TIME)  # Wait for the VM to revert
        return path_to_vm

    def stop_emulator(self, path_to_vm: str, region=None, *args, **kwargs):
        # Note: region parameter is ignored for VMware provider
        # but kept for interface consistency with other providers
        logger.info("Stopping VMware VM...")
        VMwareProvider._execute_command(["vmrun"] + get_vmrun_type(return_list=True) + ["stop", path_to_vm])
        time.sleep(WAIT_TIME)  # Wait for the VM to stop
