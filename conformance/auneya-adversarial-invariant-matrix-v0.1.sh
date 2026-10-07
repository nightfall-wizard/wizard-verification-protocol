#!/usr/bin/env bash
set -euo pipefail

DOC="docs/auneya/AUNEYA-ADVERSARIAL-INVARIANT-MATRIX-V0.1.md"
LEGAL="docs/auneya/AUNEYA-L1-LEGAL-BOUNDARY-V0.1.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$DOC" ] || fail "Missing $DOC"
[ -f "$LEGAL" ] || fail "Missing $LEGAL"

need() {
  grep -Fq "$1" "$DOC" || fail "Missing required text: $1"
}

need "compatible with AUNEYA L1 Legal Boundary v0.1"
need "Research-mode invariant set"
need "No token sale"
need "No market-value claim"
need "Witness cannot custody assets or authorize user state alone"
need "Economic features are disabled in research mode"
need "Legal boundary compatibility is mandatory"
need "AUNEYA-INV-001"
need "AUNEYA-INV-016"

python3 - <<'PY'
from pathlib import Path
import re
import sys

doc = Path("docs/auneya/AUNEYA-ADVERSARIAL-INVARIANT-MATRIX-V0.1.md")
text = doc.read_text(encoding="utf-8", errors="ignore")

ids = sorted(set(re.findall(r"AUNEYA-INV-\d{3}", text)))
expected = [f"AUNEYA-INV-{i:03d}" for i in range(1, 17)]

missing = [x for x in expected if x not in ids]
if missing:
    print("Missing invariant IDs: " + ", ".join(missing), file=sys.stderr)
    sys.exit(1)

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
    "must not",
    "non-value",
    "hard stop",
    "legal boundary",
    "separate legal review",
    "research mode",
]

errors = []

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

print("PASS: AUNEYA adversarial invariant matrix conformance")
PY

echo "PASS: $DOC"
