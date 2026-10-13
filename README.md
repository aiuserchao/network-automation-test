# netauto — Juniper (JunOS) network automation toolkit

Config automation + compliance check for JunOS devices, operated by Muse via chat.

## How it works

```
inventory/devices.json      # source of truth: devices, groups, variables
        |
templates/junos/*.j2        # Jinja2 templates (JunOS set-format)
        |
netauto/render.py           # render intended config per device
        |
netauto/driver.py           # pyez (real JunOS via NETCONF) or mock (file-backed fake)
        |
netauto/deploy.py           # load candidate -> show diff -> commit (only with --commit)
netauto/compliance.py       # intended vs running -> MISSING / EXTRA report
```

## Quickstart

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# render intended configs
.venv/bin/python -m netauto.render --out rendered

# compliance check against mock devices (no real hardware needed)
.venv/bin/python -m netauto.seed_mock          # inject drift into mock devices
.venv/bin/python -m netauto.compliance --transport mock

# deploy (dry run shows diff; --commit applies)
.venv/bin/python -m netauto.deploy --transport mock --device jnpr-core-01
.venv/bin/python -m netauto.deploy --transport mock --device jnpr-core-01 --commit

# full demo
bash demo.sh
```

## Against real JunOS devices

```bash
export NETAUTO_USER=netops            # or --user
export NETAUTO_PASSWORD=...           # or --key-file / NETAUTO_KEY_FILE
.venv/bin/python -m netauto.compliance --transport pyez --device 192.0.2.11
.venv/bin/python -m netauto.deploy --transport pyez --device 192.0.2.11   # dry run
.venv/bin/python -m netauto.deploy --transport pyez --device 192.0.2.11 --commit
```

Credentials come from environment / CLI flags only — never commit them to the repo.

## Chat-driven workflow (Muse operates it)

- "检查所有设备的 SNMP 合规性" → `compliance --area snmp`
- "给 core 组加个 NTP 服务器" → edit inventory → render → deploy (dry run diff first)
- "jnpr-access-01 的 drift 修一下" → `deploy --device jnpr-access-01 --commit` (after your OK)
- Compliance reports come back as MISSING / EXTRA lists; Muse explains and suggests fixes.

## Safety

- `deploy` is dry-run by default; nothing changes without `--commit`.
- Compliance never auto-removes EXTRA lines; it only reports them.
- Mock transport (`mock_state/`) mirrors the driver interface so the full flow
  is testable on machines without JunOS hardware/images.

## Roadmap

- More JunOS templates (protocols/BGP, firewall filters, VLANs)
- Scheduled compliance runs with alerting
- Rollback support on deploy (`--rollback`)
- Config backup (`show configuration | display set` snapshots in git)
