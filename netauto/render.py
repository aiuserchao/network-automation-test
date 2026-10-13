"""Render intended JunOS configs (set-format) from inventory + Jinja2 templates."""
import argparse

from jinja2 import Environment, FileSystemLoader

from . import BASE
from .inventory import get_device, resolve_devices

TEMPLATE_DIR = BASE / "templates" / "junos"
RENDERED_DIR = BASE / "rendered"
ALL_TEMPLATES = ["system.j2", "snmp.j2", "interfaces.j2"]


def normalize_set_config(text):
    """Split set-format config into clean, comparable lines."""
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _env():
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_device(device, templates=None):
    env = _env()
    parts = []
    for name in templates or ALL_TEMPLATES:
        text = env.get_template(name).render(**device)
        parts.extend(normalize_set_config(text))
    return "\n".join(parts) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render intended JunOS configs")
    ap.add_argument("--device", help="hostname or mgmt IP (default: all)")
    ap.add_argument("--out", default=str(RENDERED_DIR), help="output directory")
    args = ap.parse_args(argv)

    devices = resolve_devices()
    if args.device:
        devices = [get_device(args.device)]
    from pathlib import Path

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for dev in devices:
        text = render_device(dev)
        path = out / f"{dev['hostname']}.set"
        path.write_text(text)
        print(f"rendered {dev['hostname']}: {len(text.splitlines())} lines -> {path}")


if __name__ == "__main__":
    main()
