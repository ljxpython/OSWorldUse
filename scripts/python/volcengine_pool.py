from __future__ import annotations

import argparse
import json
import os
import sys


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from scripts.python.cua_local_targets import load_repo_dotenv


load_repo_dotenv(ROOT_DIR)


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return parsed


def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect and prewarm the Volcengine OSWorld ECS pool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show pool instances and local leases")
    status_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    ensure_parser = subparsers.add_parser("ensure", help="Ensure the pool has at least N instances")
    ensure_parser.add_argument("--size", type=_positive_int, required=True, help="Target pool size")
    ensure_parser.add_argument("--screen_width", "--screen-width", type=_positive_int, default=1920)
    ensure_parser.add_argument("--screen_height", "--screen-height", type=_positive_int, default=1080)
    ensure_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    release_parser = subparsers.add_parser("release-lease", help="Release a local lease without deleting ECS")
    release_parser.add_argument("instance_id", help="Volcengine ECS instance id")
    release_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    return parser.parse_args()


def _require_pool_enabled() -> None:
    if os.environ.get("VOLCENGINE_POOL_ENABLED", "").lower() not in {"1", "true", "yes", "on"}:
        raise SystemExit("VOLCENGINE_POOL_ENABLED=1 is required for volcengine_pool.py")


def _instance_to_dict(instance, leased_ids: set[str]) -> dict:
    eip_address = getattr(instance, "eip_address", None)
    network_interfaces = getattr(instance, "network_interfaces", None) or []
    private_ip = (
        getattr(network_interfaces[0], "primary_ip_address", None)
        if network_interfaces
        else None
    )
    tags = {
        getattr(tag, "key", ""): getattr(tag, "value", "")
        for tag in (getattr(instance, "tags", None) or [])
        if getattr(tag, "key", "")
    }
    instance_id = getattr(instance, "instance_id", "")
    return {
        "instance_id": instance_id,
        "status": getattr(instance, "status", None),
        "image_id": getattr(instance, "image_id", None),
        "zone_id": getattr(instance, "zone_id", None),
        "public_ip": getattr(eip_address, "ip_address", None) if eip_address else None,
        "private_ip": private_ip,
        "leased": instance_id in leased_ids,
        "tags": tags,
    }


def _pool_snapshot() -> dict:
    from desktop_env.providers.volcengine.manager import (
        VOLCENGINE_IMAGE_ID,
        VOLCENGINE_POOL_NAME,
        VOLCENGINE_REGION,
        VolcengineVMManager,
        _clean_pool_registry,
        _list_pool_instances,
        _load_pool_registry,
        _write_pool_registry,
    )

    manager = VolcengineVMManager()
    registry = _clean_pool_registry(_load_pool_registry())
    _write_pool_registry(registry)
    leased_ids = set(registry)
    instances = [
        _instance_to_dict(instance, leased_ids)
        for instance in _list_pool_instances(manager.client, statuses=None)
    ]
    instance_ids = {item["instance_id"] for item in instances}
    free_ids = [item["instance_id"] for item in instances if not item["leased"]]
    pool_leased_ids = sorted(instance_ids & leased_ids)
    orphan_lease_ids = sorted(leased_ids - instance_ids)
    return {
        "region": VOLCENGINE_REGION,
        "pool": VOLCENGINE_POOL_NAME,
        "image_id": VOLCENGINE_IMAGE_ID,
        "total": len(instances),
        "free": len(free_ids),
        "leased": len(pool_leased_ids),
        "orphan_leases": len(orphan_lease_ids),
        "free_ids": free_ids,
        "leased_ids": pool_leased_ids,
        "orphan_lease_ids": orphan_lease_ids,
        "leases": registry,
        "instances": instances,
    }


def _print_snapshot(snapshot: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True))
        return

    print(f"region={snapshot['region']}")
    print(f"pool={snapshot['pool']}")
    print(f"image_id={snapshot['image_id']}")
    print(
        f"total={snapshot['total']} free={snapshot['free']} "
        f"leased={snapshot['leased']} orphan_leases={snapshot['orphan_leases']}"
    )
    for instance in snapshot["instances"]:
        lease_state = "leased" if instance["leased"] else "free"
        print(
            "instance={instance_id} status={status} state={state} public_ip={public_ip} private_ip={private_ip}".format(
                instance_id=instance["instance_id"],
                status=instance["status"],
                state=lease_state,
                public_ip=instance["public_ip"] or "",
                private_ip=instance["private_ip"] or "",
            )
        )


def run() -> int:
    args = config()
    _require_pool_enabled()

    if args.command == "status":
        _print_snapshot(_pool_snapshot(), args.json)
        return 0

    if args.command == "ensure":
        from desktop_env.providers.volcengine.manager import VolcengineVMManager

        manager = VolcengineVMManager()
        ids = manager.ensure_pool_size(
            target_size=args.size,
            screen_size=(args.screen_width, args.screen_height),
        )
        snapshot = _pool_snapshot()
        snapshot["ensured_ids"] = ids
        _print_snapshot(snapshot, args.json)
        return 0

    if args.command == "release-lease":
        from desktop_env.providers.volcengine.manager import release_pool_vm

        release_pool_vm(args.instance_id)
        snapshot = _pool_snapshot()
        snapshot["released_instance_id"] = args.instance_id
        _print_snapshot(snapshot, args.json)
        return 0

    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(run())
