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
need find
need wc
need tr
need sort
need git
need gh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REPO="${GH_REPO:-${GITHUB_REPOSITORY:-nightfall-wizard/wizard-verification-protocol}}"
TOOL="tools/wvp-release-reality-check.sh"
SCHEMA="schemas/wvp-release-reality-check-v0.1.schema.json"
DOC="docs/WVP-RELEASE-REALITY-CHECK-V0.1.md"
WF=".github/workflows/wvp-release-reality-check.yml"
ALIGN="conformance/wvp-release-reality-schema-output-alignment.sh"
FIXTURE_GATE="conformance/wvp-release-reality-deterministic-fixture-gate.sh"

test -x "$TOOL" || fail "Release-Reality Tool fehlt oder ist nicht ausführbar."
test -f "$SCHEMA" || fail "Schema fehlt."
test -f "$DOC" || fail "Dokumentation fehlt."
test -f "$WF" || fail "Workflow fehlt."
test -x "$ALIGN" || fail "Schema/Output Alignment Gate fehlt oder ist nicht ausführbar."
test -x "$FIXTURE_GATE" || fail "Deterministic Fixture Gate fehlt oder ist nicht ausführbar."

bash -n "$TOOL"
bash -n "$ALIGN"
bash -n "$FIXTURE_GATE"

fixture_count="$(
  find fixtures/release-reality -mindepth 2 -maxdepth 2 -name input.json \
    | sort \
    | wc -l \
    | tr -d ' '
)"

[[ "$fixture_count" == "8" ]] || fail "Erwartet 8 Fixture-Dateien, gefunden: $fixture_count"

for expected in \
  fixtures/release-reality/RR-001-repo-with-release/input.json \
  fixtures/release-reality/RR-002-repo-without-release/input.json \
  fixtures/release-reality/RR-003-checksum-no-signature/input.json \
  fixtures/release-reality/RR-004-signature-no-checksum/input.json \
  fixtures/release-reality/RR-005-public-key-no-signature/input.json \
  fixtures/release-reality/RR-006-missing-security-md/input.json \
  fixtures/release-reality/RR-007-invalid-repo-format/input.json \
  fixtures/release-reality/RR-008-release-api-not-verifiable/input.json
do
  test -f "$expected" || fail "Fixture fehlt: $expected"
done

"$ALIGN"
"$FIXTURE_GATE"

OUT="$(mktemp "${TMPDIR:-/tmp}/wvp-step22e-live.XXXXXX.json")"
trap 'rm -f "$OUT"' EXIT

WVP_CHECKED_AT="${WVP_CHECKED_AT:-2026-10-06T00:00:00Z}" \
  "$TOOL" "$REPO" --out "$OUT"

jq -e '
  .schema_version == "wvp-release-reality-check/v0.1" and
  (.target.repository | type == "string") and
  (.release_evidence.asset_names | type == "array") and
  (.repository_evidence.security_md_found | type == "boolean") and
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
  (.explicit_non_claims | index("not_an_audit") != null) and
  (.explicit_non_claims | index("not_investment_advice") != null)
' "$OUT" >/dev/null || fail "Live-Output verletzt STEP-22E-Post-Merge-Grenzen."

echo "PASS: WVP release-reality post-merge verification"
