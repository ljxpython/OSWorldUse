import logging
import os
import platform
import subprocess
import time
import ipaddress

from desktop_env.providers.base import Provider

logger = logging.getLogger("desktopenv.providers.vmware.VMwareProvider")
logger.setLevel(logging.INFO)

WAIT_TIME = 3


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

    def start_emulator(self, path_to_vm: str, headless: bool, os_type: str):
        print("Starting VMware VM...")
        logger.info("Starting VMware VM...")

        normalized_path_to_vm = os.path.abspath(os.path.normpath(path_to_vm))
        if not os.path.exists(normalized_path_to_vm):
            raise FileNotFoundError(
                f"VMX not found: {normalized_path_to_vm}. "
                "If you manually deleted vmware_vm_data, remove stale entries in .vmware_vms or rerun to re-install the VM."
            )

        while True:
            try:
                output = subprocess.check_output(f"vmrun {get_vmrun_type()} list", shell=True, stderr=subprocess.STDOUT)
                output = output.decode()
                output = output.splitlines()

                if any(os.path.abspath(os.path.normpath(line)) == normalized_path_to_vm for line in output):
                    logger.info("VM is running.")
                    break
                else:
                    logger.info("Starting VM...")
                    _command = ["vmrun"] + get_vmrun_type(return_list=True) + ["start", normalized_path_to_vm]
                    if headless:
                        _command.append("nogui")
                    VMwareProvider._execute_command(_command)
                    time.sleep(WAIT_TIME)

            except subprocess.CalledProcessError as e:
                logger.error(f"Error executing command: {e.output.decode().strip()}")

    def get_ip_address(self, path_to_vm: str) -> str:
        logger.info("Getting VMware VM IP address...")
        normalized_path_to_vm = os.path.abspath(os.path.normpath(path_to_vm))
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

                if result.returncode != 0:
                    logger.warning(
                        "Failed to get VMware VM IP address, returncode=%s, stderr=%s",
                        result.returncode,
                        error or "<empty>",
                    )
                    time.sleep(WAIT_TIME)
                    continue

                if not output or output.lower() == "unknown":
                    logger.info("VMware VM IP address is not ready yet: %s", output or "<empty>")
                    time.sleep(WAIT_TIME)
                    continue

                try:
                    ipaddress.ip_address(output)
                except ValueError:
                    logger.warning("VMware VM returned invalid IP address: %s", output)
                    time.sleep(WAIT_TIME)
                    continue

                logger.info(f"VMware VM IP address: {output}")
                return output
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
