import os

from desktop_env.providers.base import VMManager


class RemoteVMManager(VMManager):
    """Manager for an existing remote OSWorld machine.

    This manager does not allocate machines. It only returns a configured
    endpoint when DesktopEnv is created without an explicit path_to_vm.
    """

    def initialize_registry(self, **kwargs):
        return None

    def add_vm(self, vm_path, **kwargs):
        return None

    def delete_vm(self, vm_path, **kwargs):
        return None

    def occupy_vm(self, vm_path, pid, **kwargs):
        return None

    def list_free_vms(self, **kwargs):
        endpoint = os.environ.get("OSWORLD_REMOTE_VM")
        return [endpoint] if endpoint else []

    def check_and_clean(self, **kwargs):
        return None

    def get_vm_path(self, **kwargs):
        endpoint = os.environ.get("OSWORLD_REMOTE_VM")
        if not endpoint:
            raise ValueError(
                "Remote provider needs --path_to_vm or OSWORLD_REMOTE_VM. "
                "Use host[:server_port[:chromium_port[:vnc_port[:vlc_port]]]]."
            )
        return endpoint

