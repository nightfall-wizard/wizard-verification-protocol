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

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TOOL="tools/wvp-release-reality-check.sh"
SCHEMA="schemas/wvp-release-reality-check-v0.1.schema.json"
REPO="${GH_REPO:-${GITHUB_REPOSITORY:-nightfall-wizard/wizard-verification-protocol}}"

test -x "$TOOL" || fail "Tool fehlt oder ist nicht ausführbar: $TOOL"
test -f "$SCHEMA" || fail "Schema fehlt: $SCHEMA"

bash -n "$TOOL"

OUT="$(mktemp "${TMPDIR:-/tmp}/wvp-release-reality-output.XXXXXX.json")"
trap 'rm -f "$OUT"' EXIT

WVP_CHECKED_AT="${WVP_CHECKED_AT:-2026-10-06T00:00:00Z}" \
  "$TOOL" "$REPO" --out "$OUT"

jq -e '
  .type == "object" and
  (.required | index("schema_version") != null) and
  (.required | index("checked_at") != null) and
  (.required | index("target") != null) and
  (.required | index("release_evidence") != null) and
  (.required | index("repository_evidence") != null) and
  (.required | index("claim_status") != null) and
  (.required | index("risk_level") != null) and
  (.required | index("explicit_non_claims") != null)
' "$SCHEMA" >/dev/null || fail "Schema-Top-Level ist nicht stabil."

jq -e '
  .schema_version == "wvp-release-reality-check/v0.1" and
  (.checked_at | type == "string") and
  (.target.repository | type == "string") and
  (.target.repository_found | type == "boolean") and
  (.target.default_branch | type == "string") and
  (.target.visibility | type == "string") and
  (.target.archived | type == "boolean") and
  (.target.fork | type == "boolean") and
  (.release_evidence.latest_public_release_found | type == "boolean") and
  (.release_evidence.tag_ref_found | type == "boolean") and
  (.release_evidence.asset_count | type == "number") and
  (.release_evidence.asset_names | type == "array") and
  (.release_evidence.checksum_asset_found | type == "boolean") and
  (.release_evidence.signature_asset_found | type == "boolean") and
  (.repository_evidence.security_md_found | type == "boolean") and
  (.repository_evidence.readme_found | type == "boolean") and
  (.repository_evidence.license_found | type == "boolean") and
  (.repository_evidence.github_workflow_found | type == "boolean") and
  (.claim_status.repository_exists | type == "string") and
  (.claim_status.latest_public_release_exists | type == "string") and
  (.claim_status.release_tag_ref_exists | type == "string") and
  (.claim_status.checksum_asset_presence | type == "string") and
  (.claim_status.signature_asset_presence | type == "string") and
  .claim_status.checksum_validation == "not_proven" and
  .claim_status.signature_validation == "not_proven" and
  .claim_status.source_to_binary_correspondence == "not_proven" and
  .claim_status.reproducible_build == "not_proven" and
  .claim_status.binary_safety == "not_proven" and
  .claim_status.protocol_security == "not_proven" and
  .claim_status.audit_status == "not_proven" and
  .claim_status.legal_clearance == "not_proven" and
  .claim_status.investment_quality == "not_proven" and
  .claim_status.custody_safety == "not_proven" and
  (.explicit_non_claims | type == "array") and
  (.explicit_non_claims | index("not_an_audit") != null) and
  (.explicit_non_claims | index("not_investment_advice") != null)
' "$OUT" >/dev/null || fail "Output passt nicht zur stabilen WVP-v0.1-Form."

echo "PASS: WVP release-reality schema/output alignment"
