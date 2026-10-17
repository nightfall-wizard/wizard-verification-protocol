#!/usr/bin/env bash
set -Eeuo pipefail

REPO="nightfall-wizard/wizard-verification-protocol"
TAG="v0.4.0"
ARCHIVE="wvp-v0.4.0-source.tar.gz"
CHECKSUM="$ARCHIVE.sha256"
MANIFEST="WVP-v0.4.0-MANIFEST.json"
fail() { echo "FAIL: WVP v0.4.0 lifecycle: $*" >&2; exit 1; }

command -v git >/dev/null || fail "git missing"
command -v gh >/dev/null || fail "gh missing"
command -v jq >/dev/null || fail "jq missing"
command -v sha256sum >/dev/null || fail "sha256sum missing"

ref="$(git ls-remote --tags origin "refs/tags/$TAG" "refs/tags/$TAG^{}")" ||
  fail "Cannot inspect remote tag"
release_json="$(mktemp)"
temp_dir="$(mktemp -d)"
trap 'rm -f "$release_json"; rm -rf "$temp_dir"' EXIT

if [ -z "$ref" ]; then
  if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    fail "GitHub release exists without the Git tag"
  fi
  echo "PASS: v0.4.0 has no tag and no publicly readable release (pre-publication)"
  exit 0
fi

# Once tagged, a published release must exist; no fallback to pre-release gates.
gh release view "$TAG" --repo "$REPO" \
  --json tagName,isDraft,isPrerelease,assets > "$release_json" ||
  fail "tag exists but GitHub release is unavailable"
jq -e --arg tag "$TAG" '
  .tagName == $tag and
  .isDraft == false and
  .isPrerelease == false and
  ([.assets[].name] | length) == ([.assets[].name] | unique | length) and
  ([.assets[].name | select(endswith(".sha256"))] | length) == 1 and
  ([.assets[].name | select(endswith(".sig"))] | length) <= 1
' "$release_json" >/dev/null || fail "ambiguous, draft or prerelease assets"

gh release download "$TAG" --repo "$REPO" --dir "$temp_dir" \
  --pattern "$MANIFEST" --pattern "$ARCHIVE" \
  --pattern "$CHECKSUM" || fail "cannot download release evidence"

for item in "$MANIFEST" "$ARCHIVE" "$CHECKSUM"; do
  [ -s "$temp_dir/$item" ] || fail "missing artifact: $item"
done
(cd "$temp_dir" && sha256sum -c "$CHECKSUM") ||
  fail "source checksum mismatch"

sha="$(sha256sum "$temp_dir/$ARCHIVE" | cut -d' ' -f1)"
ref_commit="$(printf '%s\n' "$ref" | awk '$2 ~ /\^\{\}$/ {print $1; exit}')"
if [ -z "$ref_commit" ]; then
  ref_commit="$(printf '%s\n' "$ref" | awk '$2 == "refs/tags/v0.4.0" {print $1; exit}')"
fi
[ -n "$ref_commit" ] || fail "cannot resolve release tag commit"

jq -e --arg sha "$sha" --arg commit "$ref_commit" --arg tag "$TAG" '
  .tag == $tag and
  .source_commit == $commit and
  .source_archive_sha256 == $sha and
  .independent_audit_claim == false and
  .reproducible_build_claim == false and
  .source_to_release_proof_claim == false and
  .binary_safety_claim == false and
  (.signed_android_binary | type == "boolean")
' "$temp_dir/$MANIFEST" >/dev/null || fail "manifest/provenance mismatch"

# Independently compare the published Cargo.lock to manifest, without
# confusing its hash with the local, potentially newer main commit.
git fetch -q --no-tags --depth=1 origin "refs/tags/$TAG" ||
  fail "cannot fetch released source"
lockhash="$(git show FETCH_HEAD:Cargo.lock | sha256sum | cut -d' ' -f1)"
jq -e --arg lock "$lockhash" '.cargo_lock_sha256 == $lock' \
  "$temp_dir/$MANIFEST" >/dev/null || fail "Cargo.lock provenance mismatch"
git show FETCH_HEAD:reference/rust/wvp-release-check/Cargo.toml |
  grep -qx 'version = "0.4.0"' || fail "tagged version does not match"

if jq -e '.signed_android_binary == true' "$temp_dir/$MANIFEST" >/dev/null; then
  bin="wvp-release-check-v0.4.0-termux-android-aarch64"
  jq -e --arg bin "$bin" '
    ([.assets[].name | select(. == $bin)] | length) == 1 and
    ([.assets[].name | select(. == ($bin + ".sha256"))] | length) == 1 and
    ([.assets[].name | select(. == ($bin + ".sig"))] | length) == 1 and
    ([.assets[].name | select(. == "wvp-release-signing-public-rsa3072.pem")] | length) == 1
  ' "$release_json" >/dev/null || fail "signed binary manifest lacks required assets"
  gh release download "$TAG" --repo "$REPO" --dir "$temp_dir" \
    --pattern "$bin" --pattern "$bin.sha256" --pattern "$bin.sig" \
    --pattern "wvp-release-signing-public-rsa3072.pem" ||
    fail "cannot download signed binary evidence"
  (cd "$temp_dir" && sha256sum -c "$bin.sha256") ||
    fail "binary checksum verification failed"
  openssl dgst -sha256 -verify "$temp_dir/wvp-release-signing-public-rsa3072.pem" \
    -signature "$temp_dir/$bin.sig" "$temp_dir/$bin" |
    grep -qx "Verified OK" || fail "binary signature verification failed"
else
  jq -e '
    ([.assets[].name | select(endswith(".sig"))] | length) == 0 and
    ([.assets[].name | select(. == "wvp-v0.4.0-source.tar.gz.sha256")] | length) == 1
  ' "$release_json" >/dev/null || fail "source-only release must not claim signature"
fi

echo "PASS: published v0.4.0 tag, manifest, source checksum, package version and bounded signature claims"
