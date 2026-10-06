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
need find
need sort
need wc
need tr
need grep

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

INDEX="capabilities/wvp-release-reality-capability-index-v0.1.json"
DOC="docs/WVP-RELEASE-REALITY-CAPABILITY-INDEX-V0.1.md"

test -f "$INDEX" || fail "Capability Index fehlt."
test -f "$DOC" || fail "Capability Index Dokumentation fehlt."

jq -e '
  .schema_version == "wvp-release-reality-capability-index/v0.1" and
  .subsystem == "wvp-release-reality-check" and
  .subsystem_version == "v0.1" and
  .status == "implemented" and
  (.capabilities | type == "array") and
  (.explicit_non_capabilities | type == "array") and
  (.gates | type == "array") and
  (.fixtures | type == "array") and
  (.hard_rules | type == "array") and
  (.claim_status_values | type == "array")
' "$INDEX" >/dev/null || fail "Grundstruktur ungültig."

jq -e '
  (.capabilities | length) >= 10 and
  (.explicit_non_capabilities | length) >= 10 and
  (.gates | length) == 4 and
  (.fixtures | length) == 8 and
  (.hard_rules | length) >= 8
' "$INDEX" >/dev/null || fail "Capability Index unvollständig."

for capability in \
  repository_metadata_visibility \
  release_metadata_visibility \
  tag_reference_presence \
  checksum_asset_presence \
  signature_asset_presence \
  public_verification_key_asset_presence \
  repository_hygiene_metadata \
  schema_output_alignment_gate \
  deterministic_fixture_gate \
  post_merge_verification_gate
do
  jq -e --arg capability "$capability" '
    .capabilities | map(.id) | index($capability) != null
  ' "$INDEX" >/dev/null || fail "Capability fehlt: $capability"
done

for non_capability in \
  audit_status_proof \
  legal_clearance_proof \
  investment_quality_assessment \
  custody_safety_proof \
  binary_safety_proof \
  source_to_binary_correspondence_proof \
  reproducible_build_proof \
  protocol_security_proof \
  checksum_validation \
  signature_validation
do
  jq -e --arg non_capability "$non_capability" '
    .explicit_non_capabilities | index($non_capability) != null
  ' "$INDEX" >/dev/null || fail "Non-Capability fehlt: $non_capability"
done

for rule in \
  public_verification_key_is_not_detached_signature \
  metadata_presence_is_not_validation \
  release_presence_is_not_audit \
  signature_asset_presence_is_not_signature_validation \
  checksum_asset_presence_is_not_checksum_validation \
  no_private_keys_or_seeds \
  no_wallet_or_custody_data \
  no_investment_or_legal_advice
do
  jq -e --arg rule "$rule" '
    .hard_rules | index($rule) != null
  ' "$INDEX" >/dev/null || fail "Hard Rule fehlt: $rule"
done

for gate in $(jq -r '.gates[]' "$INDEX"); do
  test -f "$gate" || fail "Gate-Datei fehlt: $gate"
done

for fixture in $(jq -r '.fixtures[]' "$INDEX"); do
  test -f "$fixture" || fail "Fixture-Datei fehlt: $fixture"
done

fixture_count="$(
  find fixtures/release-reality -mindepth 2 -maxdepth 2 -name input.json \
    | sort \
    | wc -l \
    | tr -d ' '
)"

[[ "$fixture_count" == "8" ]] || fail "Erwartet 8 Fixtures, gefunden: $fixture_count"

jq -e '
  (.claim_status_values | index("proven") != null) and
  (.claim_status_values | index("not_enough_evidence") != null) and
  (.claim_status_values | index("not_verifiable") != null) and
  (.claim_status_values | index("not_proven") != null)
' "$INDEX" >/dev/null || fail "Claim-Status-Werte unvollständig."

grep -q "not a release approval" "$DOC" || fail "Dokumentation muss klarstellen, dass dies keine Release-Freigabe ist."
grep -q "not a detached signature" "$DOC" || fail "Dokumentation muss Public-Key-vs-Signature-Grenze nennen."

echo "PASS: WVP release-reality capability index gate"
