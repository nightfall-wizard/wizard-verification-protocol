#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

fail() {
  echo "FEHLER: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Benötigtes Tool fehlt: $1"
}

usage() {
  cat >&2 <<'USAGE'
Usage:
  tools/wvp-release-reality-check.sh owner/repo --out report.json

Boundary:
  Records public GitHub evidence only.
  Does not prove audit status, legal clearance, investment quality, custody safety,
  binary safety, source-to-binary correspondence, protocol security or reproducible builds.
USAGE
}

need_cmd gh
need_cmd jq
need_cmd date
need_cmd mktemp
need_cmd grep

TARGET_REPO="${1:-}"
[[ -n "$TARGET_REPO" ]] || { usage; exit 2; }
shift || true

OUT="-"

while (($#)); do
  case "$1" in
    --out)
      shift || fail "--out benötigt einen Pfad."
      OUT="${1:-}"
      [[ -n "$OUT" ]] || fail "--out benötigt einen Pfad."
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unbekanntes Argument: $1"
      ;;
  esac
  shift || true
done

[[ "$TARGET_REPO" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || fail "Ungültiges Repo-Format. Erwartet: owner/repo"

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/wvp-release-reality.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

api_ok() {
  local endpoint="$1"
  local out="$2"
  local err="$3"
  gh api "$endpoint" >"$out" 2>"$err"
}

status_from_bool() {
  if [[ "$1" == true ]]; then
    printf 'proven'
  else
    printf 'not_enough_evidence'
  fi
}

CHECKED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

REPO_JSON="$TMP_DIR/repo.json"
REPO_ERR="$TMP_DIR/repo.err"
RELEASES_JSON="$TMP_DIR/releases.json"
RELEASES_ERR="$TMP_DIR/releases.err"
WORKFLOWS_JSON="$TMP_DIR/workflows.json"
WORKFLOWS_ERR="$TMP_DIR/workflows.err"

repo_found=false
default_branch=""
visibility="unknown"
archived=false
fork=false

if api_ok "repos/${TARGET_REPO}" "$REPO_JSON" "$REPO_ERR"; then
  repo_found=true
  default_branch="$(jq -r '.default_branch // ""' "$REPO_JSON")"
  visibility="$(jq -r '.visibility // "unknown"' "$REPO_JSON")"
  archived="$(jq -r '.archived // false' "$REPO_JSON")"
  fork="$(jq -r '.fork // false' "$REPO_JSON")"
fi

release_found=false
release_not_verifiable=false
release_tag=""
release_name=""
release_draft=false
release_prerelease=false
assets_count=0
asset_names_json='[]'
checksum_asset_found=false
signature_asset_found=false

if [[ "$repo_found" == true ]]; then
  if api_ok "repos/${TARGET_REPO}/releases?per_page=20" "$RELEASES_JSON" "$RELEASES_ERR"; then
    if jq -e 'map(select(.draft == false)) | length > 0' "$RELEASES_JSON" >/dev/null; then
      release_found=true
      release_tag="$(jq -r 'map(select(.draft == false)) | first | .tag_name // ""' "$RELEASES_JSON")"
      release_name="$(jq -r 'map(select(.draft == false)) | first | .name // ""' "$RELEASES_JSON")"
      release_draft="$(jq -r 'map(select(.draft == false)) | first | .draft // false' "$RELEASES_JSON")"
      release_prerelease="$(jq -r 'map(select(.draft == false)) | first | .prerelease // false' "$RELEASES_JSON")"
      assets_count="$(jq -r 'map(select(.draft == false)) | first | (.assets // []) | length' "$RELEASES_JSON")"
      asset_names_json="$(jq -c 'map(select(.draft == false)) | first | (.assets // []) | map(.name)' "$RELEASES_JSON")"

      if jq -r 'map(select(.draft == false)) | first | (.assets // []) | map(.name) | .[]?' "$RELEASES_JSON" | grep -Eiq '(^|[-_.])(sha256|sha512|checksum|checksums|sums)([-_.]|$)|SHA256SUMS|SHA512SUMS'; then
        checksum_asset_found=true
      fi

      if jq -r 'map(select(.draft == false)) | first | (.assets // []) | map(.name) | .[]?' "$RELEASES_JSON" | grep -Eiq '(\.asc$|\.sig$|\.minisig$|\.sigstore$|\.bundle$|\.pem$)'; then
        signature_asset_found=true
      fi
    fi
  else
    release_not_verifiable=true
  fi
fi

tag_ref_found=false
tag_ref_status="not_enough_evidence"

if [[ "$release_found" == true && -n "$release_tag" ]]; then
  TAGS_JSON="$TMP_DIR/tags.json"
  TAGS_ERR="$TMP_DIR/tags.err"
  if api_ok "repos/${TARGET_REPO}/git/matching-refs/tags/${release_tag}" "$TAGS_JSON" "$TAGS_ERR"; then
    if jq -e --arg tag "refs/tags/${release_tag}" 'map(select(.ref == $tag)) | length > 0' "$TAGS_JSON" >/dev/null; then
      tag_ref_found=true
      tag_ref_status="proven"
    fi
  else
    tag_ref_status="not_verifiable"
  fi
fi

security_md_found=false
readme_found=false
license_found=false
workflow_found=false

if [[ "$repo_found" == true && -n "$default_branch" ]]; then
  for candidate in SECURITY.md .github/SECURITY.md docs/SECURITY.md; do
    if api_ok "repos/${TARGET_REPO}/contents/${candidate}?ref=${default_branch}" "$TMP_DIR/security.json" "$TMP_DIR/security.err"; then
      security_md_found=true
      break
    fi
  done

  for candidate in README.md README.rst README.txt; do
    if api_ok "repos/${TARGET_REPO}/contents/${candidate}?ref=${default_branch}" "$TMP_DIR/readme.json" "$TMP_DIR/readme.err"; then
      readme_found=true
      break
    fi
  done

  for candidate in LICENSE LICENSE.md LICENSE.txt COPYING; do
    if api_ok "repos/${TARGET_REPO}/contents/${candidate}?ref=${default_branch}" "$TMP_DIR/license.json" "$TMP_DIR/license.err"; then
      license_found=true
      break
    fi
  done

  if api_ok "repos/${TARGET_REPO}/contents/.github/workflows?ref=${default_branch}" "$WORKFLOWS_JSON" "$WORKFLOWS_ERR"; then
    if jq -e 'type == "array" and length > 0' "$WORKFLOWS_JSON" >/dev/null; then
      workflow_found=true
    fi
  fi
fi

repo_status="$(status_from_bool "$repo_found")"
release_status="$(status_from_bool "$release_found")"
[[ "$release_not_verifiable" == true ]] && release_status="not_verifiable"

checksum_status="$(status_from_bool "$checksum_asset_found")"
signature_status="$(status_from_bool "$signature_asset_found")"
security_status="$(status_from_bool "$security_md_found")"
readme_status="$(status_from_bool "$readme_found")"
license_status="$(status_from_bool "$license_found")"
workflow_status="$(status_from_bool "$workflow_found")"

risk_level="evidence_incomplete"
if [[ "$repo_found" == true && "$release_found" == true && "$checksum_asset_found" == true && "$signature_asset_found" == true && "$security_md_found" == true && "$workflow_found" == true ]]; then
  risk_level="basic_release_evidence_present"
fi

RESULT="$(jq -n \
  --arg schema_version "wvp-release-reality-check/v0.1" \
  --arg checked_at "$CHECKED_AT" \
  --arg target_repo "$TARGET_REPO" \
  --arg default_branch "$default_branch" \
  --arg visibility "$visibility" \
  --arg release_tag "$release_tag" \
  --arg release_name "$release_name" \
  --arg repo_status "$repo_status" \
  --arg release_status "$release_status" \
  --arg tag_ref_status "$tag_ref_status" \
  --arg checksum_status "$checksum_status" \
  --arg signature_status "$signature_status" \
  --arg security_status "$security_status" \
  --arg readme_status "$readme_status" \
  --arg license_status "$license_status" \
  --arg workflow_status "$workflow_status" \
  --arg risk_level "$risk_level" \
  --argjson repo_found "$repo_found" \
  --argjson archived "$archived" \
  --argjson fork "$fork" \
  --argjson release_found "$release_found" \
  --argjson release_draft "$release_draft" \
  --argjson release_prerelease "$release_prerelease" \
  --argjson assets_count "$assets_count" \
  --argjson asset_names "$asset_names_json" \
  --argjson checksum_asset_found "$checksum_asset_found" \
  --argjson signature_asset_found "$signature_asset_found" \
  --argjson tag_ref_found "$tag_ref_found" \
  --argjson security_md_found "$security_md_found" \
  --argjson readme_found "$readme_found" \
  --argjson license_found "$license_found" \
  --argjson workflow_found "$workflow_found" \
  '{
    schema_version: $schema_version,
    checked_at: $checked_at,
    target: {
      repository: $target_repo,
      repository_found: $repo_found,
      default_branch: $default_branch,
      visibility: $visibility,
      archived: $archived,
      fork: $fork
    },
    release_evidence: {
      latest_public_release_found: $release_found,
      tag_name: $release_tag,
      release_name: $release_name,
      draft: $release_draft,
      prerelease: $release_prerelease,
      tag_ref_found: $tag_ref_found,
      asset_count: $assets_count,
      asset_names: $asset_names,
      checksum_asset_found: $checksum_asset_found,
      signature_asset_found: $signature_asset_found
    },
    repository_evidence: {
      security_md_found: $security_md_found,
      readme_found: $readme_found,
      license_found: $license_found,
      github_workflow_found: $workflow_found
    },
    claim_status: {
      repository_exists: $repo_status,
      latest_public_release_exists: $release_status,
      release_tag_ref_exists: $tag_ref_status,
      checksum_asset_presence: $checksum_status,
      signature_asset_presence: $signature_status,
      security_policy_presence: $security_status,
      readme_presence: $readme_status,
      license_presence: $license_status,
      ci_workflow_presence: $workflow_status,
      checksum_validation: "not_proven",
      signature_validation: "not_proven",
      source_to_binary_correspondence: "not_proven",
      reproducible_build: "not_proven",
      binary_safety: "not_proven",
      protocol_security: "not_proven",
      audit_status: "not_proven",
      legal_clearance: "not_proven",
      investment_quality: "not_proven",
      custody_safety: "not_proven"
    },
    risk_level: $risk_level,
    explicit_non_claims: [
      "not_an_audit",
      "not_legal_clearance",
      "not_investment_advice",
      "not_custody_safety_proof",
      "not_binary_safety_proof",
      "not_source_to_binary_proof",
      "not_reproducible_build_proof",
      "not_protocol_security_proof"
    ]
  }'
)"

if [[ "$OUT" == "-" ]]; then
  printf '%s\n' "$RESULT"
else
  mkdir -p "$(dirname "$OUT")"
  printf '%s\n' "$RESULT" >"$OUT"
fi
