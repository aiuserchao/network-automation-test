"""Inventory loader: JSON source of truth, group vars merged under host vars."""
import json

from . import BASE

INVENTORY_FILE = BASE / "inventory" / "devices.json"


def load_inventory(path=INVENTORY_FILE):
    with open(path) as f:
        return json.load(f)


def resolve_devices(inv=None):
    """Return devices with group vars merged under host vars (host wins)."""
    inv = inv or load_inventory()
    groups = inv.get("groups", {})
    devices = []
    for d in inv.get("devices", []):
        merged = {}
        merged.update(groups.get(d.get("group", ""), {}))
        merged.update(d.get("vars", {}))
        merged["hostname"] = d["hostname"]
        merged["mgmt_ip"] = d["mgmt_ip"]
        merged["group"] = d.get("group", "")
        merged["role"] = d.get("role", "")
        devices.append(merged)
    return devices


def get_device(hostname_or_ip, inv=None):
    for d in resolve_devices(inv):
        if d["hostname"] == hostname_or_ip or d["mgmt_ip"] == hostname_or_ip:
            return d
    raise KeyError(f"device not found in inventory: {hostname_or_ip}")
