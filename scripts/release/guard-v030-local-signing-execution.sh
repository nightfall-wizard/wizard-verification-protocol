#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 LOCAL SIGNING EXECUTION GUARD ==="

START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

MODE="${1:---evaluate}"

case "$MODE" in
  --evaluate|--require-ready)
    ;;
  *)
    echo "FAIL: unsupported mode: $MODE"
    echo "Usage:"
    echo "  $0 --evaluate"
    echo "  $0 --require-ready"
    exit 1
    ;;
esac

TARGET_REPO="nightfall-wizard/wizard-verification-protocol"
VERSION="0.3.0"
TAG="v0.3.0"

STAGE_CHECK="conformance/release-check-v030-unsigned-asset-staging.sh"
SIGN_CHECK="conformance/release-check-v030-detached-signature-procedure.sh"

STAGE_DIR="target/wvp-release-v0.3.0-unsigned"
ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"
ASSET="$STAGE_DIR/$ASSET_NAME"
CHECKSUM="$STAGE_DIR/$ASSET_NAME.sha256"
SIGNATURE="$STAGE_DIR/$ASSET_NAME.sig"
STAGING_MANIFEST="$STAGE_DIR/STAGING-MANIFEST.json"

REPORT_DIR="target/wvp-v0.3.0-local-signing-execution-guard"
REPORT="$REPORT_DIR/GUARD-REPORT.json"

mkdir -p "$REPORT_DIR"

echo "Mode: $MODE"
echo

echo "=== RUN REQUIRED SAFE PRECHECKS ==="
chmod +x "$STAGE_CHECK" "$SIGN_CHECK"

"$STAGE_CHECK"
STAGE_RESULT=0

"$SIGN_CHECK"
SIGN_DRY_RUN_RESULT=0
echo

echo "=== COLLECT GUARD STATE ==="
HEAD_SHA="$(git rev-parse HEAD)"
BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"

if [ -n "$(git status --porcelain)" ]; then
  TREE_CLEAN=false
else
  TREE_CLEAN=true
fi

if git rev-parse --verify origin/main >/dev/null 2>&1; then
  ORIGIN_MAIN_SHA="$(git rev-parse origin/main)"
else
  ORIGIN_MAIN_SHA=""
fi

if [ -n "$ORIGIN_MAIN_SHA" ] && [ "$HEAD_SHA" = "$ORIGIN_MAIN_SHA" ]; then
  HEAD_MATCHES_ORIGIN_MAIN=true
else
  HEAD_MATCHES_ORIGIN_MAIN=false
fi

if git tag --list | grep -qx "$TAG"; then
  LOCAL_TAG_EXISTS=true
else
  LOCAL_TAG_EXISTS=false
fi

if [ -e "$SIGNATURE" ]; then
  SIGNATURE_EXISTS=true
else
  SIGNATURE_EXISTS=false
fi

if [ -x "$ASSET" ]; then
  ASSET_EXISTS=true
else
  ASSET_EXISTS=false
fi

if [ -s "$CHECKSUM" ]; then
  CHECKSUM_EXISTS=true
else
  CHECKSUM_EXISTS=false
fi

if [ -s "$STAGING_MANIFEST" ]; then
  MANIFEST_EXISTS=true
else
  MANIFEST_EXISTS=false
fi

MANIFEST_SOURCE_COMMIT=""
MANIFEST_SOURCE_DIRTY=""
MANIFEST_SIGNATURE_CREATED=""
MANIFEST_TAG_CREATED=""
MANIFEST_RELEASE_CREATED=""
MANIFEST_STAGE_ONLY=""

if [ "$MANIFEST_EXISTS" = true ]; then
  MANIFEST_SOURCE_COMMIT="$(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data.get("source", {}).get("git_commit", ""))
PY
)"
  MANIFEST_SOURCE_DIRTY="$(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(data.get("source", {}).get("dirty", "")).lower())
PY
)"
  MANIFEST_SIGNATURE_CREATED="$(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(data.get("signature_created", "")).lower())
PY
)"
  MANIFEST_TAG_CREATED="$(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(data.get("tag_created", "")).lower())
PY
)"
  MANIFEST_RELEASE_CREATED="$(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(data.get("github_release_created", "")).lower())
PY
)"
  MANIFEST_STAGE_ONLY="$(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(data.get("staging_only", "")).lower())
PY
)"
fi

if [ "$MANIFEST_SOURCE_COMMIT" = "$HEAD_SHA" ]; then
  MANIFEST_COMMIT_MATCH=true
else
  MANIFEST_COMMIT_MATCH=false
fi

if [ "$MANIFEST_SOURCE_DIRTY" = "false" ]; then
  MANIFEST_CLEAN_SOURCE=true
else
  MANIFEST_CLEAN_SOURCE=false
fi

if [ "$MANIFEST_SIGNATURE_CREATED" = "false" ]; then
  MANIFEST_NO_SIGNATURE=true
else
  MANIFEST_NO_SIGNATURE=false
fi

if [ "$MANIFEST_TAG_CREATED" = "false" ]; then
  MANIFEST_NO_TAG=true
else
  MANIFEST_NO_TAG=false
fi

if [ "$MANIFEST_RELEASE_CREATED" = "false" ]; then
  MANIFEST_NO_RELEASE=true
else
  MANIFEST_NO_RELEASE=false
fi

if [ "$MANIFEST_STAGE_ONLY" = "true" ]; then
  MANIFEST_STAGE_ONLY_OK=true
else
  MANIFEST_STAGE_ONLY_OK=false
fi

APPROVED=true
BLOCKERS=()

if [ "$TREE_CLEAN" != true ]; then
  APPROVED=false
  BLOCKERS+=("source tree is dirty")
fi

if [ "$HEAD_MATCHES_ORIGIN_MAIN" != true ]; then
  APPROVED=false
  BLOCKERS+=("HEAD does not match origin/main or origin/main is unavailable")
fi

if [ "$LOCAL_TAG_EXISTS" = true ]; then
  APPROVED=false
  BLOCKERS+=("local v0.3.0 tag already exists")
fi

if [ "$SIGNATURE_EXISTS" = true ]; then
  APPROVED=false
  BLOCKERS+=("detached signature already exists")
fi

if [ "$ASSET_EXISTS" != true ]; then
  APPROVED=false
  BLOCKERS+=("staged asset missing")
fi

if [ "$CHECKSUM_EXISTS" != true ]; then
  APPROVED=false
  BLOCKERS+=("staged checksum missing")
fi

if [ "$MANIFEST_EXISTS" != true ]; then
  APPROVED=false
  BLOCKERS+=("staging manifest missing")
fi

if [ "$MANIFEST_COMMIT_MATCH" != true ]; then
  APPROVED=false
  BLOCKERS+=("staging manifest source commit does not match HEAD")
fi

if [ "$MANIFEST_CLEAN_SOURCE" != true ]; then
  APPROVED=false
  BLOCKERS+=("staging manifest was generated from dirty source tree")
fi

if [ "$MANIFEST_NO_SIGNATURE" != true ]; then
  APPROVED=false
  BLOCKERS+=("staging manifest indicates signature was created")
fi

if [ "$MANIFEST_NO_TAG" != true ]; then
  APPROVED=false
  BLOCKERS+=("staging manifest indicates tag was created")
fi

if [ "$MANIFEST_NO_RELEASE" != true ]; then
  APPROVED=false
  BLOCKERS+=("staging manifest indicates GitHub release was created")
fi

if [ "$MANIFEST_STAGE_ONLY_OK" != true ]; then
  APPROVED=false
  BLOCKERS+=("staging manifest does not mark staging_only true")
fi

echo "Tree clean: $TREE_CLEAN"
echo "HEAD: $HEAD_SHA"
echo "origin/main: $ORIGIN_MAIN_SHA"
echo "HEAD matches origin/main: $HEAD_MATCHES_ORIGIN_MAIN"
echo "Local tag exists: $LOCAL_TAG_EXISTS"
echo "Signature exists: $SIGNATURE_EXISTS"
echo "Manifest commit match: $MANIFEST_COMMIT_MATCH"
echo "Manifest clean source: $MANIFEST_CLEAN_SOURCE"
echo "Approved for local signing: $APPROVED"
echo

echo "=== WRITE GUARD REPORT ==="
python3 - "$REPORT" \
  "$VERSION" \
  "$TAG" \
  "$MODE" \
  "$HEAD_SHA" \
  "$BRANCH_NAME" \
  "$ORIGIN_MAIN_SHA" \
  "$TREE_CLEAN" \
  "$HEAD_MATCHES_ORIGIN_MAIN" \
  "$LOCAL_TAG_EXISTS" \
  "$SIGNATURE_EXISTS" \
  "$ASSET_EXISTS" \
  "$CHECKSUM_EXISTS" \
  "$MANIFEST_EXISTS" \
  "$MANIFEST_COMMIT_MATCH" \
  "$MANIFEST_CLEAN_SOURCE" \
  "$MANIFEST_NO_SIGNATURE" \
  "$MANIFEST_NO_TAG" \
  "$MANIFEST_NO_RELEASE" \
  "$MANIFEST_STAGE_ONLY_OK" \
  "$APPROVED" \
  "${BLOCKERS[@]}" <<'PY'
import json
import sys
from pathlib import Path

def b(value: str) -> bool:
    return value == "true"

report_path = Path(sys.argv[1])

data = {
    "tool": "wvp-release-check",
    "package_version": sys.argv[2],
    "planned_tag": sys.argv[3],
    "evidence_type": "local-signing-execution-guard",
    "mode": sys.argv[4],
    "signing_executed": False,
    "signature_created": False,
    "tag_created": False,
    "github_release_created": False,
    "source_to_release_proof": False,
    "reproducible_build_claim": False,
    "binary_safety_claim": False,
    "audit_claim": False,
    "source": {
        "git_commit": sys.argv[5],
        "git_branch": sys.argv[6],
        "origin_main": sys.argv[7],
        "tree_clean": b(sys.argv[8]),
        "head_matches_origin_main": b(sys.argv[9]),
    },
    "checks": {
        "local_tag_exists": b(sys.argv[10]),
        "signature_exists": b(sys.argv[11]),
        "asset_exists": b(sys.argv[12]),
        "checksum_exists": b(sys.argv[13]),
        "manifest_exists": b(sys.argv[14]),
        "manifest_commit_match": b(sys.argv[15]),
        "manifest_clean_source": b(sys.argv[16]),
        "manifest_no_signature": b(sys.argv[17]),
        "manifest_no_tag": b(sys.argv[18]),
        "manifest_no_release": b(sys.argv[19]),
        "manifest_stage_only": b(sys.argv[20]),
    },
    "approved_for_local_signing": b(sys.argv[21]),
    "blockers": list(sys.argv[22:]),
    "limitations": [
        "this guard does not create a signature",
        "this guard does not create a tag",
        "this guard does not create a GitHub release",
        "local signing approval is not a reproducible-build proof",
        "local signing approval is not a source-to-release proof",
        "local signing approval is not a binary safety proof",
        "no audit claim is made",
    ],
}

report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(report_path)
PY

cat "$REPORT"
echo

echo "=== VERIFY GUARD REPORT NON-CLAIMS ==="
grep -q '"evidence_type": "local-signing-execution-guard"' "$REPORT"
grep -q '"signing_executed": false' "$REPORT"
grep -q '"signature_created": false' "$REPORT"
grep -q '"tag_created": false' "$REPORT"
grep -q '"github_release_created": false' "$REPORT"
grep -q '"source_to_release_proof": false' "$REPORT"
grep -q '"reproducible_build_claim": false' "$REPORT"
grep -q '"binary_safety_claim": false' "$REPORT"
grep -q '"audit_claim": false' "$REPORT"
echo "Guard report non-claims OK."
echo

if [ "$MODE" = "--require-ready" ] && [ "$APPROVED" != true ]; then
  echo "FAIL: local signing is not approved."
  printf 'Blockers:\n'
  printf ' - %s\n' "${BLOCKERS[@]}"
  exit 1
fi

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3.0 LOCAL SIGNING EXECUTION GUARD RESULT ==="
echo "RESULT: PASS"
echo "Mode: $MODE"
echo "Approved for local signing: $APPROVED"
echo "Signing executed: no"
echo "Signature created: no"
echo "Tag created: no"
echo "GitHub release created: no"
echo "Report: $REPORT"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
