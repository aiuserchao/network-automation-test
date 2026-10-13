"""Seed mock devices with drifted running-configs for demo/testing.

Takes the rendered intended config, then injects drift:
  - removes the snmp community line (something someone forgot to configure)
  - adds a rogue interface description (unapproved manual change)
"""
from . import BASE
from .inventory import resolve_devices
from .render import normalize_set_config, render_device


def main():
    state_dir = BASE / "mock_state"
    state_dir.mkdir(parents=True, exist_ok=True)
    for dev in resolve_devices():
        lines = normalize_set_config(render_device(dev))
        drifted = [l for l in lines if not l.startswith("set snmp community")]
        drifted.append('set interfaces ge-0/0/9 description "ROGUE unapproved uplink"')
        (state_dir / f"{dev['hostname']}.set").write_text(
            "\n".join(sorted(drifted)) + "\n"
        )
        print(f"seeded {dev['hostname']}: {len(drifted)} lines (drift injected)")


if __name__ == "__main__":
    main()
