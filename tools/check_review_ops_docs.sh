#!/usr/bin/env bash
set -Eeuo pipefail

MARKER="WVP-REVIEW-OPS-V1"

required_files=(
  "docs/review/README.md"
  "docs/review/EXTERNAL-REVIEW-PROCESS.md"
  "docs/review/REVIEWER-CHECKLIST.md"
  "docs/review/REVIEW-REQUEST-TEMPLATE.md"
  "docs/review/MAINTAINER-RESPONSE-PROTOCOL.md"
  "docs/review/REVIEW-OPS-EVIDENCE.json"
  "docs/review/BOUNDARY-GLOSSARY.md"
)

for f in "${required_files[@]}"; do
  if [ ! -f "$f" ]; then
    echo "FAIL: missing $f"
    exit 1
  fi
done

for f in "${required_files[@]}"; do
  if [ "$f" != "docs/review/README.md" ]; then
    if ! grep -q "$MARKER" "$f"; then
      echo "FAIL: marker missing in $f"
      exit 1
    fi
  fi
done

required_terms=(
  "formal GitHub"
  "Approve"
  "Request changes"
  "no Nightfall safety certification"
  "no cryptographic audit"
  "no financial"
  "no investment"
  "no custody"
  "no bounty"
  "no token"
  "admin bypass"
)

for term in "${required_terms[@]}"; do
  if ! grep -Riq "$term" docs/review; then
    echo "FAIL: required review-ops term missing: $term"
    exit 1
  fi
done

python3 -m json.tool docs/review/REVIEW-OPS-EVIDENCE.json >/dev/null

echo "PASS: review operations docs are complete and bounded"
