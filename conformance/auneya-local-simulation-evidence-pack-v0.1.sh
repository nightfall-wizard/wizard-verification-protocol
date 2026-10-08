#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Simulation Evidence Pack v0.1 Conformance ==="

python3 tools/auneya/auneya_local_simulation_evidence_pack.py

JSON_OUT="reports/auneya/local-simulation-v0.1/AUNEYA-LOCAL-SIMULATION-EVIDENCE-v0.1.json"
MD_OUT="reports/auneya/local-simulation-v0.1/AUNEYA-LOCAL-SIMULATION-EVIDENCE-v0.1.md"

test -f "$JSON_OUT"
test -f "$MD_OUT"

python3 - <<'PY2'
import json
import sys
from pathlib import Path

path = Path("reports/auneya/local-simulation-v0.1/AUNEYA-LOCAL-SIMULATION-EVIDENCE-v0.1.json")
obj = json.loads(path.read_text("utf-8"))

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if obj.get("evidence_pack") != "auneya-local-simulation-evidence-v0.1":
    fail("wrong evidence_pack")

if obj.get("overall_status") != "pass":
    failed = [c.get("id") for c in obj.get("checks", []) if c.get("status") != "pass"]
    fail("failed checks: " + ", ".join(failed))

for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
    if obj.get(key) is not False:
        fail(key + " must be false")

required = {
    "claim_schema",
    "witness_proof_schema",
    "event_schema",
    "pulse_flow",
    "local_witness_runner",
    "one_command_local_demo",
    "local_demo_boundary_validation",
    "invalid_private_claim_rejected",
}

seen = {c.get("id"): c.get("status") for c in obj.get("checks", [])}

missing = sorted(required - set(seen))
if missing:
    fail("missing required checks: " + ", ".join(missing))

bad = sorted(k for k in required if seen.get(k) != "pass")
if bad:
    fail("required checks not pass: " + ", ".join(bad))

print("PASS AUNEYA Local Simulation Evidence Pack v0.1 JSON validation")
PY2

grep -q "Status: PASS" "$MD_OUT"
grep -q "Mainnet active: false" "$MD_OUT"
grep -q "Token created: false" "$MD_OUT"
grep -q "Market value claimed: false" "$MD_OUT"
grep -q "Transferable: false" "$MD_OUT"

echo "PASS AUNEYA Local Simulation Evidence Pack v0.1 conformance"
