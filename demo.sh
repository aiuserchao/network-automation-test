#!/bin/bash
# End-to-end demo on mock JunOS devices:
#   render -> seed drift -> compliance (shows drift) -> deploy --commit -> compliance (clean)
set -e
cd "$(dirname "$0")"
PY=.venv/bin/python

echo "=== 1. render intended configs ==="
$PY -m netauto.render --out rendered

echo ""
echo "=== 2. seed mock devices with drift ==="
$PY -m netauto.seed_mock

echo ""
echo "=== 3. compliance check (expect NON-COMPLIANT) ==="
$PY -m netauto.compliance --transport mock || true

echo ""
echo "=== 4. deploy to jnpr-core-01 (dry run first) ==="
$PY -m netauto.deploy --transport mock --device jnpr-core-01

echo ""
echo "=== 5. deploy --commit jnpr-core-01 ==="
$PY -m netauto.deploy --transport mock --device jnpr-core-01 --commit

echo ""
echo "=== 6. compliance check again (jnpr-core-01 should be clean) ==="
$PY -m netauto.compliance --transport mock --device jnpr-core-01
