#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "ABBRUCH in Zeile $LINENO. Bitte die letzte Fehlermeldung pruefen." >&2' ERR

REPO="nightfall-wizard/wizard-verification-protocol"
TAG="v0.4.0"
fail() { echo "FEHLER: $*" >&2; exit 1; }
for tool in git gh jq python3 cargo rustc sha256sum openssl gzip tar; do
  command -v "$tool" >/dev/null || fail "Fehlendes Werkzeug: $tool"
done
command -v pkg >/dev/null || fail "Dieses Skript ist fuer Termux."
cd "$(git rev-parse --show-toplevel)"
[ "$(git branch --show-current)" = main ] || fail "Branch muss main sein."
[ -z "$(git status --porcelain)" ] || fail "Git-Quellbaum ist nicht sauber."
gh auth status >/dev/null 2>&1 || fail "Zuerst gh auth login ausfuehren."
[ "$(gh api user --jq '.login')" = nightfall-wizard ] || fail "Falscher GitHub-Account."
[ "$(gh api "repos/$REPO" --jq '.permissions.push')" = true ] || fail "Keine Push-Berechtigung."
SHA="$(git rev-parse HEAD)"
[ "$(git ls-remote origin refs/heads/main | cut -f1)" = "$SHA" ] || fail "Lokaler main ist nicht aktuell."

check_ci() {
  local commit="$1" data i
  for i in $(seq 1 90); do
    data="$(gh api "repos/$REPO/commits/$commit/check-runs?per_page=100")" || fail "CI nicht abrufbar."
    if printf '%s\n' "$data" | jq -e '
      [.check_runs[] | select(
        .name == "required" or .name == "security-invariants" or
        .name == "Rust reference implementations" or .name == "verify" or
        .name == "release-reality-check")] as $c |
      ([$c[].name] | unique | length) == 5 and
      all($c[]; .status == "completed" and .conclusion == "success")
    ' >/dev/null; then
      echo "PASS: 5/5 erforderliche CI-Checks fuer $commit"
      return 0
    fi
    if printf '%s\n' "$data" | jq -e '
      any(.check_runs[];
        (.name == "required" or .name == "security-invariants" or
         .name == "Rust reference implementations" or .name == "verify" or
         .name == "release-reality-check") and
        .status == "completed" and .conclusion != "success")
    ' >/dev/null; then fail "Erforderliche CI fehlgeschlagen."; fi
    [ "$i" -lt 90 ] || fail "CI-Zeitlimit."
    sleep 20
  done
}

python3 - <<'PY'
import tomllib
from pathlib import Path
pkg=tomllib.loads(Path("reference/rust/wvp-release-check/Cargo.toml").read_text())["package"]
rows=tomllib.loads(Path("Cargo.lock").read_text())["package"]
assert pkg["version"]=="0.4.0"
assert sum(x["name"]=="wvp-release-check" and x["version"]=="0.4.0" for x in rows)==1
print("PASS: Paketversion 0.4.0 und Cargo.lock.")
PY
check_ci "$SHA"
REMOTE_TAG="$(git ls-remote --tags origin "refs/tags/$TAG" "refs/tags/$TAG^{}")"
if [ -n "$REMOTE_TAG" ]; then
  git fetch -q origin "refs/tags/$TAG:refs/tags/$TAG"
  [ "$(git rev-parse "$TAG^{}")" = "$SHA" ] || fail "Tag zeigt auf einen anderen Commit."
else
  if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
    fail "Release existiert ohne passenden Tag."
  fi
  echo "=== VOLLSTAENDIGE RELEASE-GATES ==="
  cargo fmt --all -- --check
  cargo clippy --workspace --all-targets -- -D warnings
  cargo test --workspace --locked
  python3 -m unittest discover -s tests -q
  bash tools/check_release_quality_gate.sh
  for gate in \
    conformance/wvp-v040-version-conformance.sh \
    conformance/wvp-v040-release-check-fixture-runner-report-conformance.sh \
    conformance/wvp-v040-release-readiness-checklist-conformance.sh \
    conformance/wvp-v040-release-notes-draft-conformance.sh \
    conformance/wvp-v040-final-pre-release-gate-conformance.sh \
    conformance/wvp-v040-controlled-release-plan-conformance.sh \
    conformance/wvp-v040-pre-release-prep-stop-marker-conformance.sh \
    conformance/wvp-v040-public-status-alignment-conformance.sh
  do
    bash "$gate"
  done
fi

STAGE="$(mktemp -d "$HOME/wvp-v040-assets.XXXXXXXX")"
ARCHIVE="wvp-v0.4.0-source.tar.gz"
git archive --format=tar --prefix=wvp-v0.4.0/ HEAD | gzip -n -9 > "$STAGE/$ARCHIVE"
gzip -t "$STAGE/$ARCHIVE"
SOURCE_SHA="$(sha256sum "$STAGE/$ARCHIVE" | cut -d' ' -f1)"
LOCK_SHA="$(sha256sum Cargo.lock | cut -d' ' -f1)"
SIGNED=false
KEY="${WVP_SIGNING_KEY:-$HOME/.config/wvp/release-signing-private.pem}"
PUB="keys/release/wvp-release-signing-public.pem"
if [ -f "$KEY" ]; then
  [ "$(uname -m)" = aarch64 ] || fail "Android-Binary erfordert aarch64."
  [ -r "$KEY" ] && [ -s "$PUB" ] || fail "Signaturmaterial unvollstaendig."
  case "$(readlink -f "$KEY")" in "$PWD"/*) fail "Privater Schluessel im Repository.";; esac
  PERM="$(stat -c %a "$KEY")"
  [ "$((8#$PERM & 077))" -eq 0 ] || fail "Signierschluessel braucht chmod 600."
  PRIVATE_FP="$(openssl pkey -in "$KEY" -passin pass: -pubout -outform DER | sha256sum | cut -d' ' -f1)"
  PUBLIC_FP="$(openssl pkey -pubin -in "$PUB" -pubout -outform DER | sha256sum | cut -d' ' -f1)"
  [ "$PRIVATE_FP" = "$PUBLIC_FP" ] || fail "Falscher Signierschluessel."
  cargo build --release --locked
  BIN="wvp-release-check-v0.4.0-termux-android-aarch64"
  cp target/release/wvp-release-check "$STAGE/$BIN"
  chmod 755 "$STAGE/$BIN"
  (cd "$STAGE" && sha256sum "$BIN" > "$BIN.sha256" && sha256sum -c "$BIN.sha256")
  openssl dgst -sha256 -sign "$KEY" -out "$STAGE/$BIN.sig" "$STAGE/$BIN"
  openssl dgst -sha256 -verify "$PUB" -signature "$STAGE/$BIN.sig" "$STAGE/$BIN" | grep -qx "Verified OK"
  cp "$PUB" "$STAGE/wvp-release-signing-public-rsa3072.pem"
  SIGNED=true
else
  (cd "$STAGE" && sha256sum "$ARCHIVE" > "$ARCHIVE.sha256" && sha256sum -c "$ARCHIVE.sha256")
  echo "SOURCE-ONLY: Kein privater WVP-Signierschluessel vorhanden."
fi
jq -n -S --arg commit "$SHA" --arg tag "$TAG" \
  --arg source "$SOURCE_SHA" --arg lock "$LOCK_SHA" --argjson signed "$SIGNED" \
  '{project:"Wizard Verification Protocol",tag:$tag,source_commit:$commit,
    source_archive_sha256:$source,cargo_lock_sha256:$lock,
    signed_android_binary:$signed,independent_audit_claim:false,
    reproducible_build_claim:false,source_to_release_proof_claim:false,
    binary_safety_claim:false}' > "$STAGE/WVP-v0.4.0-MANIFEST.json"

# The WVP live verifier rejects duplicate checksum or signature assets.
[ "$(find "$STAGE" -maxdepth 1 -type f -name '*.sha256' | wc -l)" -eq 1 ] || fail "Mehrdeutige Pruefsummen."
[ "$(find "$STAGE" -maxdepth 1 -type f -name '*.sig' | wc -l)" -le 1 ] || fail "Mehrdeutige Signaturen."
[ -z "$(git status --porcelain)" ] || fail "Quellbaum wurde veraendert."
[ "$(git ls-remote origin refs/heads/main | cut -f1)" = "$SHA" ] || fail "main hat sich geaendert."

NOTES="$(mktemp "$HOME/wvp-v040-notes.XXXXXXXX")"
cat docs/release/WVP-V0.4.0-RELEASE.md > "$NOTES"
{
  printf '\n## Provenance\n\nSource commit: %s\nArchive SHA256: %s\n' "$SHA" "$SOURCE_SHA"
  printf 'Signed Android binary: %s\n' "$SIGNED"
  echo "CI has passed. Independent audit, binary safety and reproducible build are NOT claimed."
  if [ "$SIGNED" = false ]; then echo "Source-only release: No compiled executable or signature is distributed."; fi
} >> "$NOTES"

if [ -z "$REMOTE_TAG" ]; then
  git tag -a "$TAG" -m "WVP v0.4.0"
  git push origin "refs/tags/$TAG"
fi
if ! gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  gh release create "$TAG" "$STAGE"/* --repo "$REPO" --verify-tag \
    --title "WVP v0.4.0" --notes-file "$NOTES"
fi
[ "$(gh release view "$TAG" --repo "$REPO" --json isDraft --jq '.isDraft')" = false ] || fail "Release ist nur ein Draft."

DOWNLOAD="$(mktemp -d "$HOME/wvp-v040-verify.XXXXXXXX")"
gh release download "$TAG" --repo "$REPO" --dir "$DOWNLOAD" --clobber
cmp -s "$STAGE/$ARCHIVE" "$DOWNLOAD/$ARCHIVE" || fail "Remote-Source stimmt nicht."
[ "$(find "$DOWNLOAD" -maxdepth 1 -type f -name '*.sha256' | wc -l)" -eq 1 ] || fail "Remote: mehrere Pruefsummen."
[ "$(find "$DOWNLOAD" -maxdepth 1 -type f -name '*.sig' | wc -l)" -le 1 ] || fail "Remote: mehrere Signaturen."
SUMFILE="$(find "$DOWNLOAD" -maxdepth 1 -type f -name '*.sha256' -print -quit)"
(cd "$DOWNLOAD" && sha256sum -c "$(basename "$SUMFILE")")
if [ "$SIGNED" = true ]; then
  cmp -s "$STAGE/$BIN" "$DOWNLOAD/$BIN" || fail "Remote-Binary stimmt nicht."
  openssl dgst -sha256 -verify "$PUB" -signature "$DOWNLOAD/$BIN.sig" "$DOWNLOAD/$BIN" | grep -qx "Verified OK"
fi

if ! grep -q '<!-- WVP-V040-PUBLISHED:START -->' README.md; then
  BRANCH="docs/wvp-v040-published-$(date -u +%Y%m%dT%H%M%SZ)"
  git switch -q -c "$BRANCH"
  python3 - "$SHA" <<'PY'
from pathlib import Path
import sys
p=Path("README.md")
text=p.read_text()
needle="## Current Status\n"
assert needle in text
block=("<!-- WVP-V040-PUBLISHED:START -->\n"
       "## Current Published WVP Release\n\n"
       "**WVP v0.4.0 is published.** "
       "[GitHub Release](https://github.com/nightfall-wizard/wizard-verification-protocol/releases/tag/v0.4.0).\n\n"
       "Tagged source commit: "+sys.argv[1]+"\n\n"
       "The older v0.4 prepared-not-released section is historical, not the current status.\n"
       "No independent audit, binary-safety proof or reproducible-build proof is claimed.\n"
       "<!-- WVP-V040-PUBLISHED:END -->\n\n")
p.write_text(text.replace(needle,block+needle,1))
PY
  cat > docs/release/WVP-V0.4.0-POST-RELEASE-VERIFICATION.md <<EOF
# WVP v0.4.0 Publication Record

Release: https://github.com/$REPO/releases/tag/$TAG
Tagged source commit: $SHA
Source archive SHA256: $SOURCE_SHA
Signed Android binary: $SIGNED
Release archive re-downloaded and compared successfully.

Historical preparation records remain preserved.
No independent audit, source-to-release proof, binary safety claim or reproducible-build proof.
EOF
  git add README.md docs/release/WVP-V0.4.0-POST-RELEASE-VERIFICATION.md
  git commit -m "docs: record published WVP v0.4.0"
  git push -u origin "$BRANCH"
  PR="$(gh pr create --repo "$REPO" --base main --head "$BRANCH" \
    --title "docs: record WVP v0.4.0 publication" \
    --body "Record verified release and preserve pre-release records and safety boundaries.")"
  echo "PR: $PR"
  sleep 15
  gh pr checks "$PR" --repo "$REPO" --watch --fail-fast
  gh pr merge "$PR" --repo "$REPO" --squash --delete-branch
  DOC_SHA="$(gh pr view "$PR" --repo "$REPO" --json mergeCommit --jq '.mergeCommit.oid')"
  [ -n "$DOC_SHA" ] && [ "$DOC_SHA" != null ] || fail "Dokumentations-Merge fehlt."
  check_ci "$DOC_SHA"
fi

gh release view "$TAG" --repo "$REPO" --json tagName,url,assets \
  --jq '{release:.url,tag:.tagName,assets:[.assets[].name]}'
echo "PASS: WVP v0.4.0 publiziert, Assets verifiziert, Dokumentation gemergt."