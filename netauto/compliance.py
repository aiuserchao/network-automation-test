"""Compliance check: intended config (rendered) vs running config on device(s).

Reports, per device:
  - MISSING: in intended config but absent on device  -> needs configuring
  - EXTRA:   on device but not in intended config     -> drift / rogue config
Exit code 0 when all checked devices are compliant, 1 otherwise.
EXTRA lines are reported only, never auto-removed (safe default).
"""
import argparse
import sys

from .driver import get_driver
from .inventory import get_device, resolve_devices
from .render import normalize_set_config, render_device

AREAS = {
    "system": ["system.j2"],
    "snmp": ["snmp.j2"],
    "interfaces": ["interfaces.j2"],
}


def check_device(device, transport, areas=None, **conn):
    templates = None
    if areas:
        templates = [t for a in areas for t in AREAS[a]]
    intended = set(normalize_set_config(render_device(device, templates)))
    drv = get_driver(transport, device, **conn)
    drv.connect()
    try:
        running = set(normalize_set_config(drv.get_running_set()))
    finally:
        drv.close()
    missing = sorted(intended - running)
    extra = sorted(running - intended)
    return {
        "hostname": device["hostname"],
        "missing": missing,
        "extra": extra,
        "compliant": not missing and not extra,
    }


def print_report(result):
    h = result["hostname"]
    if result["compliant"]:
        print(f"[{h}] COMPLIANT")
        return
    print(f"[{h}] NON-COMPLIANT")
    for line in result["missing"]:
        print(f"  MISSING  {line}")
    for line in result["extra"]:
        print(f"  EXTRA    {line}   (on device, not in intended config)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="JunOS compliance check")
    ap.add_argument("--transport", choices=["mock", "pyez"], default="mock")
    ap.add_argument("--device", help="hostname or mgmt IP (default: all)")
    ap.add_argument("--area", action="append", choices=list(AREAS),
                    help="limit to area(s); repeatable (default: all)")
    ap.add_argument("--user", help="device username (or NETAUTO_USER)")
    ap.add_argument("--password", help="device password (or NETAUTO_PASSWORD)")
    ap.add_argument("--key-file", help="SSH key file (or NETAUTO_KEY_FILE)")
    args = ap.parse_args(argv)

    devices = resolve_devices()
    if args.device:
        devices = [get_device(args.device)]
    conn = {"user": args.user, "password": args.password, "key_file": args.key_file}
    results = [check_device(d, args.transport, args.area, **conn) for d in devices]
    for r in results:
        print_report(r)
    bad = sum(1 for r in results if not r["compliant"])
    print(f"\n{len(results) - bad}/{len(results)} devices compliant")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
