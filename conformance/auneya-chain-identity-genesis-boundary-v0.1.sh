#!/usr/bin/env bash
set -euo pipefail

DOC="docs/auneya/AUNEYA-CHAIN-IDENTITY-GENESIS-BOUNDARY-V0.1.md"
LEGAL="docs/auneya/AUNEYA-L1-LEGAL-BOUNDARY-V0.1.md"
MATRIX="docs/auneya/AUNEYA-ADVERSARIAL-INVARIANT-MATRIX-V0.1.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$DOC" ] || fail "Missing $DOC"
[ -f "$LEGAL" ] || fail "Missing $LEGAL"
[ -f "$MATRIX" ] || fail "Missing $MATRIX"

need() {
  grep -Fq "$1" "$DOC" || fail "Missing required text: $1"
}

need "compatible with AUNEYA L1 Legal Boundary v0.1"
need "AUNEYA Adversarial Invariant Matrix v0.1"
need "Research-mode chain identity boundary"
need "Genesis immutability boundary"
need "No token sale"
need "No market-value claim"
need "Chain id required"
need "Genesis hash required"
need "Signature domain separation"
need "Replay isolation"
need "Research-mode default"
need "No silent economic activation"
need "Legal-boundary compatibility"
need "economic_activation_enabled equals false"
need "AUNEYA-CHAIN-001"
need "AUNEYA-CHAIN-012"

python3 - <<'PY'
from pathlib import Path
import re
import sys

doc = Path("docs/auneya/AUNEYA-CHAIN-IDENTITY-GENESIS-BOUNDARY-V0.1.md")
text = doc.read_text(encoding="utf-8", errors="ignore")

expected = [f"AUNEYA-CHAIN-{i:03d}" for i in range(1, 13)]
seen = sorted(set(re.findall(r"AUNEYA-CHAIN-\d{3}", text)))

errors = []

missing = [x for x in expected if x not in seen]
extra = [x for x in seen if x not in expected]

if missing:
    errors.append("Missing chain rule IDs: " + ", ".join(missing))
if extra:
    errors.append("Unexpected chain rule IDs: " + ", ".join(extra))

rows = [line for line in text.splitlines() if line.startswith("| AUNEYA-CHAIN-")]
if len(rows) != 12:
    errors.append(f"Expected 12 chain rule rows, found {len(rows)}")

required_fields = [
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

for item in required_fields:
    if item not in text:
        errors.append("Missing required genesis field: " + item)

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

for no, line in enumerate(text.splitlines(), 1):
    low = line.lower().strip()
    if any(m in low for m in negation_markers):
        continue
    for pat in bad_patterns:
        if re.search(pat, low):
            errors.append(f"{doc}:{no}: forbidden value language: {line.strip()}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)

print("PASS: AUNEYA chain identity and genesis boundary conformance")
PY

echo "PASS: $DOC"
