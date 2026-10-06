#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

fail() {
  echo "FEHLER: $*" >&2
  exit 1
}

need() {
  command -v "$1" >/dev/null 2>&1 || fail "Tool fehlt: $1"
}

need bash
need jq
need mktemp
need cmp

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

status_from_bool() {
  if [[ "$1" == "true" ]]; then
    printf 'proven'
  else
    printf 'not_enough_evidence'
  fi
}

classify_assets() {
  local names_json="$1"

  checksum_asset_found="$(jq -nr --argjson names "$names_json" '
    $names
    | map(test("(^|[-_.])(sha256|sha512|checksum|checksums|sums)([-_.]|$)|SHA256SUMS|SHA512SUMS"; "i"))
    | any
  ')"

  signature_asset_found="$(jq -nr --argjson names "$names_json" '
    $names
    | map(test("(\\.asc$|\\.sig$|\\.minisig$|\\.sigstore$|\\.bundle$)"; "i"))
    | any
  ')"

  public_key_asset_found="$(jq -nr --argjson names "$names_json" '
    $names
    | map(test("(\\.pem$|public[-_.]?key|signing[-_.]?public|verify[-_.]?public)"; "i"))
    | any
  ')"
}

run_fixture() {
  local fixture="$1"
  local out="$2"

  local repository
  repository="$(jq -r '.target.repository // ""' "$fixture")"

  if [[ ! "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    return 2
  fi

  local repo_found default_branch visibility archived fork
  local security_md readme license workflow
  local api_verifiable release_found tag_name release_name
  local draft prerelease tag_ref_found asset_names asset_count

  repo_found="$(jq -r '.repository.found // false' "$fixture")"
  default_branch="$(jq -r '.repository.default_branch // ""' "$fixture")"
  visibility="$(jq -r '.repository.visibility // "unknown"' "$fixture")"
  archived="$(jq -r '.repository.archived // false' "$fixture")"
  fork="$(jq -r '.repository.fork // false' "$fixture")"

  security_md="$(jq -r '.repository.security_md // false' "$fixture")"
  readme="$(jq -r '.repository.readme // false' "$fixture")"
  license="$(jq -r '.repository.license // false' "$fixture")"
  workflow="$(jq -r '.repository.github_workflow // false' "$fixture")"

  api_verifiable="$(jq -r '.release.api_verifiable // true' "$fixture")"
  release_found="$(jq -r '.release.found // false' "$fixture")"
  tag_name="$(jq -r '.release.tag_name // ""' "$fixture")"
  release_name="$(jq -r '.release.release_name // ""' "$fixture")"
  draft="$(jq -r '.release.draft // false' "$fixture")"
  prerelease="$(jq -r '.release.prerelease // false' "$fixture")"
  tag_ref_found="$(jq -r '.release.tag_ref_found // false' "$fixture")"
  asset_names="$(jq -c '.release.assets // []' "$fixture")"
  asset_count="$(jq -nr --argjson names "$asset_names" '$names | length')"

  classify_assets "$asset_names"

  local repository_status release_status tag_status
  local checksum_status signature_status security_status
  local readme_status license_status workflow_status

  repository_status="$(status_from_bool "$repo_found")"

  if [[ "$api_verifiable" != "true" ]]; then
    release_status="not_verifiable"
  else
    release_status="$(status_from_bool "$release_found")"
  fi

  tag_status="$(status_from_bool "$tag_ref_found")"
  checksum_status="$(status_from_bool "$checksum_asset_found")"
  signature_status="$(status_from_bool "$signature_asset_found")"
  security_status="$(status_from_bool "$security_md")"
  readme_status="$(status_from_bool "$readme")"
  license_status="$(status_from_bool "$license")"
  workflow_status="$(status_from_bool "$workflow")"

  local risk_level
  if [[ "$repo_found" != "true" ]]; then
    risk_level="unknown_repository"
  elif [[ "$api_verifiable" != "true" ]]; then
    risk_level="release_metadata_not_verifiable"
  elif [[ "$release_found" != "true" ]]; then
    risk_level="no_release_metadata"
  elif [[ "$checksum_asset_found" != "true" || "$signature_asset_found" != "true" ]]; then
    risk_level="release_integrity_metadata_gap"
  else
    risk_level="basic_release_evidence_present"
  fi

  jq -n \
    --arg checked_at "2026-10-06T00:00:00Z" \
    --arg repository "$repository" \
    --arg default_branch "$default_branch" \
    --arg visibility "$visibility" \
    --arg tag_name "$tag_name" \
    --arg release_name "$release_name" \
    --arg repository_status "$repository_status" \
    --arg release_status "$release_status" \
    --arg tag_status "$tag_status" \
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
    --argjson draft "$draft" \
    --argjson prerelease "$prerelease" \
    --argjson tag_ref_found "$tag_ref_found" \
    --argjson asset_count "$asset_count" \
    --argjson asset_names "$asset_names" \
    --argjson checksum_asset_found "$checksum_asset_found" \
    --argjson signature_asset_found "$signature_asset_found" \
    --argjson public_key_asset_found "$public_key_asset_found" \
    --argjson security_md "$security_md" \
    --argjson readme "$readme" \
    --argjson license "$license" \
    --argjson workflow "$workflow" '
{
  schema_version: "wvp-release-reality-check/v0.1",
  checked_at: $checked_at,
  target: {
    repository: $repository,
    repository_found: $repo_found,
    default_branch: $default_branch,
    visibility: $visibility,
    archived: $archived,
    fork: $fork
  },
  release_evidence: {
    latest_public_release_found: $release_found,
    tag_name: $tag_name,
    release_name: $release_name,
    draft: $draft,
    prerelease: $prerelease,
    tag_ref_found: $tag_ref_found,
    asset_count: $asset_count,
    asset_names: $asset_names,
    checksum_asset_found: $checksum_asset_found,
    signature_asset_found: $signature_asset_found,
    public_verification_key_asset_found: $public_key_asset_found
  },
  repository_evidence: {
    security_md_found: $security_md,
    readme_found: $readme,
    license_found: $license,
    github_workflow_found: $workflow
  },
  claim_status: {
    repository_exists: $repository_status,
    latest_public_release_exists: $release_status,
    release_tag_ref_exists: $tag_status,
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
}
' > "$out"
}

expect_bool() {
  local file="$1"
  local expr="$2"
  local expected="$3"
  local label="$4"

  if [[ -z "$expected" || "$expected" == "null" ]]; then
    return 0
  fi

  jq -e --argjson expected "$expected" "$expr == \$expected" "$file" >/dev/null || \
    fail "Erwartung fehlgeschlagen: $label"
}

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/wvp-fixtures.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

for fixture in fixtures/release-reality/RR-*/input.json; do
  id="$(basename "$(dirname "$fixture")")"
  out="$TMP_DIR/${id}.json"

  invalid_expected="$(jq -r '.expected.invalid_repository // false' "$fixture")"

  if [[ "$invalid_expected" == "true" ]]; then
    if run_fixture "$fixture" "$out"; then
      fail "$id: ungültiges repository format wurde akzeptiert"
    fi
    continue
  fi

  run_fixture "$fixture" "$out"

  jq -e '.schema_version == "wvp-release-reality-check/v0.1"' "$out" >/dev/null || \
    fail "$id: falsche schema_version"

  jq -e '
    .claim_status.checksum_validation == "not_proven" and
    .claim_status.signature_validation == "not_proven" and
    .claim_status.source_to_binary_correspondence == "not_proven" and
    .claim_status.reproducible_build == "not_proven" and
    .claim_status.binary_safety == "not_proven" and
    .claim_status.protocol_security == "not_proven" and
    .claim_status.audit_status == "not_proven" and
    .claim_status.legal_clearance == "not_proven" and
    .claim_status.investment_quality == "not_proven" and
    .claim_status.custody_safety == "not_proven"
  ' "$out" >/dev/null || fail "$id: unbewiesener Claim wurde aufgewertet"

  expect_bool "$out" '.target.repository_found' \
    "$(jq -r '.expected.repository_found // empty' "$fixture")" \
    "$id repository_found"

  expect_bool "$out" '.release_evidence.latest_public_release_found' \
    "$(jq -r '.expected.release_found // empty' "$fixture")" \
    "$id release_found"

  expect_bool "$out" '.release_evidence.checksum_asset_found' \
    "$(jq -r '.expected.checksum_asset_found // empty' "$fixture")" \
    "$id checksum_asset_found"

  expect_bool "$out" '.release_evidence.signature_asset_found' \
    "$(jq -r '.expected.signature_asset_found // empty' "$fixture")" \
    "$id signature_asset_found"

  expect_bool "$out" '.release_evidence.public_verification_key_asset_found' \
    "$(jq -r '.expected.public_key_asset_found // empty' "$fixture")" \
    "$id public_key_asset_found"

  expect_bool "$out" '.repository_evidence.security_md_found' \
    "$(jq -r '.expected.security_md_found // empty' "$fixture")" \
    "$id security_md_found"
done

rr5="$TMP_DIR/RR-005-public-key-no-signature.json"
jq -e '
  .release_evidence.public_verification_key_asset_found == true and
  .release_evidence.signature_asset_found == false and
  .claim_status.signature_validation == "not_proven"
' "$rr5" >/dev/null || \
  fail "RR-005: Public Key wurde fälschlich als Signatur behandelt"

run_fixture \
  fixtures/release-reality/RR-001-repo-with-release/input.json \
  "$TMP_DIR/repeat-a.json"

run_fixture \
  fixtures/release-reality/RR-001-repo-with-release/input.json \
  "$TMP_DIR/repeat-b.json"

cmp -s "$TMP_DIR/repeat-a.json" "$TMP_DIR/repeat-b.json" || \
  fail "Fixture-Ausgabe ist nicht deterministisch"

echo "PASS: WVP release-reality deterministic fixture gate"
