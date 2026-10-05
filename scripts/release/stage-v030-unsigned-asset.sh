#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 UNSIGNED RELEASE ASSET STAGING ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

MANIFEST="reference/rust/wvp-release-check/Cargo.toml"
LOCKFILE="Cargo.lock"

VERSION="0.3.0"
TAG="v0.3.0"
TARGET_TRIPLE="termux-android-aarch64"
ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"
STAGE_DIR="target/wvp-release-v0.3.0-unsigned"

echo "=== VERIFY INPUTS ==="
test -s "$MANIFEST"
test -s "$LOCKFILE"
echo "Manifest: $MANIFEST"
echo "Lockfile: $LOCKFILE"
echo

echo "=== VERIFY PACKAGE VERSION ==="
python3 - "$MANIFEST" "$LOCKFILE" <<'PY'
from pathlib import Path
import re
import sys

manifest = Path(sys.argv[1])
lockfile = Path(sys.argv[2])

manifest_text = manifest.read_text(encoding="utf-8")
in_package = False
manifest_version = None

for line in manifest_text.splitlines():
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        in_package = stripped == "[package]"
        continue
    if in_package:
        match = re.match(r'^version\s*=\s*"([^"]+)"\s*$', stripped)
        if match:
            manifest_version = match.group(1)
            break

if manifest_version != "0.3.0":
    raise SystemExit(f"FAIL: Cargo.toml expected 0.3.0, got {manifest_version!r}")

lock_text = lockfile.read_text(encoding="utf-8")
found = False
for block in lock_text.split("[[package]]"):
    if 'name = "wvp-release-check"' in block:
        found = True
        if 'version = "0.3.0"' not in block:
            raise SystemExit("FAIL: Cargo.lock wvp-release-check entry is not 0.3.0")
        break

if not found:
    raise SystemExit("FAIL: Cargo.lock wvp-release-check entry not found")

print("Package version OK: 0.3.0")
PY
echo

echo "=== VERIFY NO TAG OR RELEASE EXECUTION ==="
if git tag --list | grep -qx "$TAG"; then
  echo "FAIL: local $TAG tag already exists. This staging step must not create a tag."
  exit 1
fi
echo "No local $TAG tag found."
echo

echo "=== BUILD RELEASE BINARY ==="
cargo build --release --locked --manifest-path "$MANIFEST"
echo

echo "=== RESOLVE BUILT BINARY ==="
BINARY=""
for candidate in \
  "target/release/wvp-release-check" \
  "reference/rust/wvp-release-check/target/release/wvp-release-check"
do
  if [ -x "$candidate" ]; then
    BINARY="$candidate"
    break
  fi
done

if [ -z "$BINARY" ]; then
  echo "FAIL: release binary not found."
  find . -path '*/release/wvp-release-check' -type f -print -exec ls -la {} \; || true
  exit 1
fi

echo "Binary: $BINARY"
echo

echo "=== PREPARE STAGING DIRECTORY ==="
mkdir -p "$STAGE_DIR"

rm -f "$STAGE_DIR/$ASSET_NAME"
rm -f "$STAGE_DIR/$ASSET_NAME.sha256"
rm -f "$STAGE_DIR/$ASSET_NAME.sig"
rm -f "$STAGE_DIR/STAGING-MANIFEST.json"

cp -f "$BINARY" "$STAGE_DIR/$ASSET_NAME"
chmod 0755 "$STAGE_DIR/$ASSET_NAME"

(
  cd "$STAGE_DIR"
  sha256sum "$ASSET_NAME" > "$ASSET_NAME.sha256"
)

echo "Staged binary: $STAGE_DIR/$ASSET_NAME"
echo "Staged checksum: $STAGE_DIR/$ASSET_NAME.sha256"
echo

echo "=== VERIFY STAGED CHECKSUM ==="
(
  cd "$STAGE_DIR"
  sha256sum -c "$ASSET_NAME.sha256"
)
echo

echo "=== VERIFY NO SIGNATURE CREATED ==="
if [ -e "$STAGE_DIR/$ASSET_NAME.sig" ]; then
  echo "FAIL: signature file exists, but this is unsigned staging."
  exit 1
fi
echo "No signature file created."
echo

echo "=== WRITE STAGING MANIFEST ==="
SOURCE_COMMIT="$(git rev-parse HEAD)"
SOURCE_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ -n "$(git status --porcelain)" ]; then
  DIRTY=true
else
  DIRTY=false
fi

BINARY_SHA256="$(sha256sum "$STAGE_DIR/$ASSET_NAME" | awk '{print $1}')"
BINARY_SIZE_BYTES="$(wc -c < "$STAGE_DIR/$ASSET_NAME" | tr -d ' ')"
LOCK_SHA256="$(sha256sum "$LOCKFILE" | awk '{print $1}')"

python3 - "$STAGE_DIR/STAGING-MANIFEST.json" <<PY
import json
from pathlib import Path

manifest = {
    "tool": "wvp-release-check",
    "package_version": "$VERSION",
    "planned_tag": "$TAG",
    "target_triple": "$TARGET_TRIPLE",
    "evidence_type": "unsigned-release-asset-staging",
    "staging_only": True,
    "tag_created": False,
    "github_release_created": False,
    "signature_created": False,
    "source_to_release_proof": False,
    "reproducible_build_claim": False,
    "binary_safety_claim": False,
    "audit_claim": False,
    "inputs": {
        "manifest": "$MANIFEST",
        "cargo_lock": "$LOCKFILE",
        "cargo_lock_sha256": "$LOCK_SHA256",
    },
    "source": {
        "git_commit": "$SOURCE_COMMIT",
        "git_branch": "$SOURCE_BRANCH",
        "dirty": ("$DIRTY" == "true"),
    },
    "outputs": {
        "stage_dir": "$STAGE_DIR",
        "asset_name": "$ASSET_NAME",
        "checksum_asset_name": "$ASSET_NAME.sha256",
        "signature_asset_name": "$ASSET_NAME.sig",
        "binary_sha256": "$BINARY_SHA256",
        "binary_size_bytes": int("$BINARY_SIZE_BYTES"),
    },
    "limitations": [
        "unsigned staging is not a published release",
        "unsigned staging is not a signature event",
        "checksum verification is integrity verification only",
        "single-machine staging does not prove source-to-release correspondence",
        "single-machine staging is not a reproducible-build proof",
        "binary safety is not proven",
        "no audit claim is made",
    ],
}
Path("$STAGE_DIR/STAGING-MANIFEST.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

cat "$STAGE_DIR/STAGING-MANIFEST.json"
echo

echo "=== VERIFY STAGING MANIFEST NON-CLAIMS ==="
grep -q '"staging_only": true' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"tag_created": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"github_release_created": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"signature_created": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"source_to_release_proof": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"reproducible_build_claim": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"binary_safety_claim": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"audit_claim": false' "$STAGE_DIR/STAGING-MANIFEST.json"
echo "Manifest non-claims OK."
echo

echo "=== VERIFY NO SECRET-LIKE MATERIAL IN STAGING ==="
BAD=0
PRIVATE_KEY_PATTERN='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?'
PRIVATE_KEY_PATTERN="${PRIVATE_KEY_PATTERN}PRIVATE KEY"
AGE_SECRET_PATTERN_A='AGE'
AGE_SECRET_PATTERN_B='-SECRET-KEY-'
GITHUB_TOKEN_PATTERN_A='ghp'
GITHUB_TOKEN_PATTERN_B='_[A-Za-z0-9_]{20,}'
SECRET_SCAN_PATTERN="${PRIVATE_KEY_PATTERN}|${AGE_SECRET_PATTERN_A}${AGE_SECRET_PATTERN_B}|${GITHUB_TOKEN_PATTERN_A}${GITHUB_TOKEN_PATTERN_B}"

while IFS= read -r f; do
  if grep -nE "$SECRET_SCAN_PATTERN" "$f"; then
    BAD=1
  fi
done <<EOF
$(find "$STAGE_DIR" -type f)
EOF

if [ "$BAD" -ne 0 ]; then
  echo "FAIL: secret-like material detected in staging directory."
  exit 1
fi
echo "No secret-like material detected in staging directory."
echo

echo "=== STAGED FILES ==="
find "$STAGE_DIR" -maxdepth 1 -type f -print -exec ls -la {} \;
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3.0 UNSIGNED RELEASE ASSET STAGING RESULT ==="
echo "RESULT: PASS"
echo "Stage directory: $STAGE_DIR"
echo "Asset: $ASSET_NAME"
echo "Checksum: $ASSET_NAME.sha256"
echo "Signature: not created"
echo "Tag: not created"
echo "GitHub release: not created"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
