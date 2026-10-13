"""Deploy intended config to device(s).

Flow per device: render -> load candidate -> show diff.
Without --commit this is a dry run (nothing changes on the device).
With --commit the candidate is committed.

Safety: never commits unless --commit is passed explicitly.
"""
import argparse
import sys

from .driver import get_driver
from .inventory import get_device, resolve_devices
from .render import render_device


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deploy intended JunOS config")
    ap.add_argument("--transport", choices=["mock", "pyez"], default="mock")
    ap.add_argument("--device", help="hostname or mgmt IP (default: all)")
    ap.add_argument("--commit", action="store_true",
                    help="actually commit (default: dry run, diff only)")
    ap.add_argument("--user", help="device username (or NETAUTO_USER)")
    ap.add_argument("--password", help="device password (or NETAUTO_PASSWORD)")
    ap.add_argument("--key-file", help="SSH key file (or NETAUTO_KEY_FILE)")
    args = ap.parse_args(argv)

    devices = resolve_devices()
    if args.device:
        devices = [get_device(args.device)]
    conn = {"user": args.user, "password": args.password, "key_file": args.key_file}
    for dev in devices:
        intended = render_device(dev)
        drv = get_driver(args.transport, dev, **conn)
        drv.connect()
        try:
            drv.load_set(intended)
            print(f"--- diff for {dev['hostname']} ---")
            print(drv.diff())
            if args.commit:
                drv.commit()
                print(f"[{dev['hostname']}] COMMITTED")
            else:
                print(f"[{dev['hostname']}] dry run: pass --commit to apply")
        finally:
            drv.close()


if __name__ == "__main__":
    main()
