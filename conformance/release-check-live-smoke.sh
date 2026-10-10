#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="nightfall-wizard/wizard-verification-protocol"
REPORT=$(mktemp)

trap 'rm -f "$REPORT"' EXIT

echo "=== LIVE RELEASE VERIFICATION ==="

cargo run --quiet \
  --manifest-path reference/rust/wvp-release-check/Cargo.toml -- \
  --target "$TARGET" \
  --json \
  --live > "$REPORT"

cat "$REPORT"

python3 - "$REPORT" <<'PY'
import json
import re
import sys
from pathlib import Path

data = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

g = data["github"]
tag = g["latest_release_tag"]

def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)

require(data["live_inspection"] is True, "not live")
require(g["repository_found"] is True, "repository")
require(g["latest_release_found"] is True, "release")
require(g["errors"] == [], "API errors")

require(
    re.fullmatch(r"(?:auneya-)?v\d+\.\d+\.\d+", tag)
    is not None,
    "unexpected release tag"
)

require(
    g["checksum_asset_count"] == 1,
    "checksum count"
)

require(
    g["checksum_verification_attempted"] is True,
    "checksum not attempted"
)

require(
    g["checksum_verification_passed"] is True,
    "checksum failed"
)

signatures = g["signature_asset_count"]

if signatures == 0:
    require(
        data["status"] == "WARN",
        "unsigned release must be WARN"
    )
    require(
        g["signature_verification_passed"] is None,
        "unexpected signature result"
    )
    print("PASS: unsigned release correctly classified")

elif signatures == 1:
    require(
        data["status"] == "INFO",
        "signed release not INFO"
    )
    require(
        g["signature_verification_passed"] is True,
        "signature verification failed"
    )
    print("PASS: signed release verified")

else:
    raise SystemExit("FAIL: duplicate signature assets")

print("LIVE INSPECTION PASS:", tag)
PY

echo
echo "=== INDEPENDENT WVP VERSION CHECK ==="

bash conformance/release-check-v030-post-release-publication.sh

echo "RESULT: PASS"
