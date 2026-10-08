#!/usr/bin/env bash
set -euo pipefail

DOC="docs/auneya/AUNEYA-L1-LEGAL-BOUNDARY-V0.1.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$DOC" ] || fail "Missing $DOC"

need() {
  grep -Fq "$1" "$DOC" || fail "Missing required text: $1"
}

need "permissionless Layer One research implementation"
need "not as an investment product"
need "No token sale."
need "No presale."
need "No allocation sale."
need "No market-value claim."
need "No profit, return, yield or appreciation claim."
need "No stablecoin peg."
need "No custody of third-party assets."
need "No exchange, broker, advice or transfer service."
need "requires separate legal review before execution"
need "the stricter non-value interpretation controls"

python3 - <<'PY'
from pathlib import Path
import re
import sys

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
    "requires separate legal review",
    "boundary",
    "hard stop",
    "not legal advice",
]

scan_paths = []

if Path("README.md").exists():
    scan_paths.append(Path("README.md"))

if Path("docs/auneya").exists():
    scan_paths.extend(sorted(Path("docs/auneya").glob("*.md")))

errors = []

for path in scan_paths:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for no, line in enumerate(text.splitlines(), 1):
        low = line.lower().strip()
        if any(m in low for m in negation_markers):
            continue
        for pat in bad_patterns:
            if re.search(pat, low):
                errors.append(f"{path}:{no}: forbidden positive value language: {line.strip()}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)

print("PASS: AUNEYA L1 legal boundary conformance")
PY

echo "PASS: $DOC"
