#!/usr/bin/env bash
set -euo pipefail

DOC="docs/auneya/AUNEYA-RESEARCH-GENESIS-SCHEMA-V0.1.md"
SCHEMA="specs/auneya/genesis/research-genesis.schema.json"
VALID="test-vectors/auneya/genesis/research-genesis.valid.json"
INVALID="test-vectors/auneya/genesis/research-genesis.invalid-economic-activation.json"
LEGAL="docs/auneya/AUNEYA-L1-LEGAL-BOUNDARY-V0.1.md"
MATRIX="docs/auneya/AUNEYA-ADVERSARIAL-INVARIANT-MATRIX-V0.1.md"
CHAIN="docs/auneya/AUNEYA-CHAIN-IDENTITY-GENESIS-BOUNDARY-V0.1.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

for f in "$DOC" "$SCHEMA" "$VALID" "$INVALID" "$LEGAL" "$MATRIX" "$CHAIN"; do
  [ -f "$f" ] || fail "Missing $f"
done

need_doc() {
  grep -Fq "$1" "$DOC" || fail "Missing required doc text: $1"
}

need_doc "compatible with AUNEYA L1 Legal Boundary v0.1"
need_doc "AUNEYA Adversarial Invariant Matrix v0.1"
need_doc "AUNEYA Chain Identity and Genesis Boundary v0.1"
need_doc "Research-mode schema"
need_doc "No token sale"
need_doc "No market-value claim"
need_doc "economic_activation_enabled"
need_doc "research_mode_enabled"

python3 - <<'PY'
from pathlib import Path
import json
import re
import sys

doc = Path("docs/auneya/AUNEYA-RESEARCH-GENESIS-SCHEMA-V0.1.md")
schema_path = Path("specs/auneya/genesis/research-genesis.schema.json")
valid_path = Path("test-vectors/auneya/genesis/research-genesis.valid.json")
invalid_path = Path("test-vectors/auneya/genesis/research-genesis.invalid-economic-activation.json")

errors = []

schema = json.loads(schema_path.read_text(encoding="utf-8"))
valid = json.loads(valid_path.read_text(encoding="utf-8"))
invalid = json.loads(invalid_path.read_text(encoding="utf-8"))

required = [
    "chain_id",
    "environment_label",
    "genesis_hash",
    "protocol_version",
    "created_at",
    "consensus_profile",
    "signature_domain",
    "witness_domain",
    "replay_domain",
    "research_mode_enabled",
    "economic_activation_enabled",
    "legal_boundary_reference",
]

if schema.get("additionalProperties") is not False:
    errors.append("Schema must set additionalProperties=false")

if schema.get("required") != required:
    errors.append("Schema required fields do not match required order/list")

props = schema.get("properties", {})

if props.get("research_mode_enabled", {}).get("const") is not True:
    errors.append("Schema must require research_mode_enabled=true")

if props.get("economic_activation_enabled", {}).get("const") is not False:
    errors.append("Schema must require economic_activation_enabled=false")

if props.get("legal_boundary_reference", {}).get("const") != "AUNEYA L1 Legal Boundary v0.1":
    errors.append("Schema must require exact legal boundary reference")

for key in required:
    if key not in valid:
        errors.append("Valid vector missing field: " + key)

if valid.get("research_mode_enabled") is not True:
    errors.append("Valid vector must keep research_mode_enabled=true")

if valid.get("economic_activation_enabled") is not False:
    errors.append("Valid vector must keep economic_activation_enabled=false")

if invalid.get("economic_activation_enabled") is not True:
    errors.append("Invalid vector must intentionally set economic_activation_enabled=true")

chain_id = valid.get("chain_id", "")
for domain_key in ["signature_domain", "witness_domain", "replay_domain"]:
    if chain_id not in str(valid.get(domain_key, "")):
        errors.append(f"Valid vector {domain_key} must include chain_id")

if invalid.get("chain_id") != chain_id:
    errors.append("Invalid vector should only vary economic activation for this fixture")

def simple_validate(instance):
    for key in required:
        if key not in instance:
            return False, f"missing {key}"

    if set(instance.keys()) != set(required):
        return False, "unexpected fields"

    if instance["research_mode_enabled"] is not True:
        return False, "research_mode_enabled must be true"

    if instance["economic_activation_enabled"] is not False:
        return False, "economic_activation_enabled must be false"

    if instance["legal_boundary_reference"] != "AUNEYA L1 Legal Boundary v0.1":
        return False, "bad legal boundary reference"

    if instance["environment_label"] not in ["research", "simulation", "devnet", "testnet"]:
        return False, "bad environment_label"

    if not re.match(r"^auneya-(research|simulation|devnet|testnet)-[a-z0-9-]+-v[0-9]+$", instance["chain_id"]):
        return False, "bad chain_id"

    if not re.match(r"^sha256:[a-f0-9]{64}$", instance["genesis_hash"]):
        return False, "bad genesis_hash"

    if not re.match(r"^0\.[0-9]+\.[0-9]+$", instance["protocol_version"]):
        return False, "bad protocol_version"

    if not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", instance["created_at"]):
        return False, "bad created_at"

    for domain_key in ["signature_domain", "witness_domain", "replay_domain"]:
        if instance["chain_id"] not in instance[domain_key]:
            return False, f"{domain_key} missing chain_id"

    return True, "ok"

ok, msg = simple_validate(valid)
if not ok:
    errors.append("Valid vector rejected: " + msg)

ok, msg = simple_validate(invalid)
if ok:
    errors.append("Invalid economic activation vector was accepted")
elif msg != "economic_activation_enabled must be false":
    errors.append("Invalid vector failed for wrong reason: " + msg)

text = doc.read_text(encoding="utf-8", errors="ignore")
combined = "\n".join([
    text,
    schema_path.read_text(encoding="utf-8", errors="ignore"),
    valid_path.read_text(encoding="utf-8", errors="ignore"),
    invalid_path.read_text(encoding="utf-8", errors="ignore"),
])

bad_patterns = [
    r"\bbuy\s+early\b",
    r"\bget\s+rich\b",
    r"\bguaranteed\s+(profit|return|yield|gain|value)\b",
    r"\bprofit\s+opportunity\b",
    r"\binvestment\s+opportunity\b",
    r"\bprice\s+target\b",
    r"\bwill\s+be\s+valuable\b",
    r"\bmarket\s+cap\s+target\b",
    r"\bexchange\s+listing\s+confirmed\b",
    r"\btoken\s+sale\s+open\b",
    r"\bpresale\s+open\b",
    r"\bstablecoin\s+peg\s+guaranteed\b",
    r"\brevenue\s+share\b",
    r"\bdividend\b",
    r"\bbuyback\b",
]

negation_markers = [
    "no ",
    "not ",
    "does not",
    "must not",
    "non-value",
    "hard stop",
    "legal boundary",
    "separate legal review",
    "research mode",
    "disabled",
    "false",
]

for no, line in enumerate(combined.splitlines(), 1):
    low = line.lower().strip()
    if any(m in low for m in negation_markers):
        continue
    for pat in bad_patterns:
        if re.search(pat, low):
            errors.append(f"forbidden value language near combined line {no}: {line.strip()}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)

print("PASS: AUNEYA research genesis schema conformance")
PY

echo "PASS: $DOC"
echo "PASS: $SCHEMA"
echo "PASS: $VALID"
echo "PASS: $INVALID"
