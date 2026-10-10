#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

trap 'printf "\nSTOP: AUNEYA-Release abgebrochen (Zeile %s).\n" "$LINENO" >&2' ERR

REPO="nightfall-wizard/wizard-verification-protocol"
TAG="auneya-v0.2.0"
BRANCH="release/auneya-v0.2.0"

echo "========================================"
echo " AUNEYA v0.2.0"
echo " INDEPENDENT MAINTAINER RELEASE"
echo "========================================"

pkg update -y
pkg install -y git gh python rust clang make openssl coreutils tar gzip

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub-Anmeldung erforderlich:"
  gh auth login --hostname github.com --git-protocol https --web
fi

gh auth setup-git

actual=$(gh api "repos/$REPO" --jq '.default_branch')

[ "$actual" = "main" ] || {
  echo "STOP: Unerwarteter Hauptbranch: $actual"
  exit 1
}

WORK=$(mktemp -d "$HOME/auneya-release-v020-XXXXXX")
OUT="$WORK/release-assets"

mkdir -p "$OUT"

printf 'Arbeitsordner: %s\n' "$WORK"

git clone --depth 1 --branch main \
  "https://github.com/$REPO.git" \
  "$WORK/source"

cd "$WORK/source"

BASE_SHA=$(git rev-parse HEAD)

[ -z "$(git status --porcelain)" ] || {
  echo "STOP: Quelle nicht sauber"
  exit 1
}

if git ls-remote --tags origin "refs/tags/$TAG" | grep -q .; then
  echo "STOP: Tag existiert bereits."
  echo "Keine Doppelveröffentlichung."
  exit 1
fi

if git ls-remote --heads origin "refs/heads/$BRANCH" | grep -q .; then
  echo "STOP: Release-Branch existiert bereits."
  echo "Keine Doppelarbeit."
  exit 1
fi

echo
echo "SOURCE SHA: $BASE_SHA"
echo
echo "========================================"
echo " AUNEYA LOCAL CONFORMANCE TESTS"
echo "========================================"

COUNT=0

{
  python3 -m compileall -q tools/auneya

  for test_file in conformance/auneya-*.sh; do

    case "$test_file" in
      *external-review*|*reviewer-packet*|*review-intake*|*recurring-review*)
        printf 'OPTIONAL: %s\n' "$test_file"
        continue
        ;;
    esac

    echo
    printf 'TEST: %s\n' "$test_file"

    bash "$test_file"

    COUNT=$((COUNT + 1))
  done

  echo
  echo "========================================"
  echo " WVP RUST CORE VERIFICATION"
  echo "========================================"

  cargo fmt --all -- --check

  cargo clippy \
    --workspace \
    --all-targets \
    --locked \
    -- -D warnings

  cargo test --workspace --locked

  echo
  echo "PASS: AUNEYA AND WVP TESTS"

} 2>&1 | tee "$OUT/self-check.log"

COUNT=$(
  find conformance \
    -maxdepth 1 \
    -type f \
    -name 'auneya-*.sh' \
    ! -name '*external-review*' \
    ! -name '*reviewer-packet*' \
    ! -name '*review-intake*' \
    ! -name '*recurring-review*' \
    | wc -l | tr -d ' '
)

git fetch origin main --quiet

CURRENT_MAIN=$(git rev-parse origin/main)

[ "$CURRENT_MAIN" = "$BASE_SHA" ] || {
  echo "STOP: main hat sich verändert."
  echo "Neue Prüfung erforderlich."
  exit 1
}

git switch -c "$BRANCH"

mkdir -p docs/auneya scripts/release

cp "$HOME/auneya-release-v020.sh" \
  scripts/release/auneya-self-release-v0.2.0-termux.sh

cat > docs/auneya/AUNEYA-RELEASE-V0.2.0.md <<EOF
# AUNEYA Local Research Preview v0.2.0

Source baseline: $BASE_SHA

Distribution version: $TAG

## Release process

- Maintainer-operated Termux release.
- Local conformance verification.
- Rust core verification.
- Source integrity checks.
- SHA-256 release checksum.
- Reproducible release documentation.

## External reviewers

External reviewer approval is not a prerequisite
for publishing this research preview.

No independent audit is claimed.

## Protocol compatibility

Existing AUNEYA v0.1 schemas remain unchanged.

## Scope

Local non-value research simulation.

No production blockchain.
No mainnet.
No actual token.
No real wallet.
No transferability.
No financial or market-value claims.

This is not a public token launch.
EOF

git add \
  docs/auneya/AUNEYA-RELEASE-V0.2.0.md \
  scripts/release/auneya-self-release-v0.2.0-termux.sh

git diff --cached --check

ACTOR=$(gh api user --jq '.login')

git \
  -c user.name="$ACTOR" \
  -c user.email="$ACTOR@users.noreply.github.com" \
  commit -m \
  'release(auneya): v0.2.0 self-validated local preview'

RELEASE_SHA=$(git rev-parse HEAD)

git \
  -c user.name="$ACTOR" \
  -c user.email="$ACTOR@users.noreply.github.com" \
  tag -a "$TAG" \
  -m "AUNEYA v0.2.0 local research preview ($RELEASE_SHA)"

ASSET="$TAG-source.tar.gz"

git archive \
  --format=tar \
  --prefix="$TAG/" \
  HEAD | gzip -n > "$OUT/$ASSET"

(
  cd "$OUT"
  sha256sum "$ASSET" > "$ASSET.sha256"
  sha256sum -c "$ASSET.sha256"
)

tar -tzf "$OUT/$ASSET" >/dev/null

cat > "$OUT/AUNEYA-SELF-CHECK-v0.2.0.txt" <<EOF
AUNEYA v0.2.0 LOCAL SELF-CHECK

Source baseline: $BASE_SHA
Release commit: $RELEASE_SHA

AUNEYA conformance tests passed: $COUNT

WVP Rust:
cargo fmt: PASS
cargo clippy: PASS
cargo test: PASS

Independent audit: NOT CLAIMED
External reviewer approval: NOT REQUIRED

Mode: LOCAL RESEARCH SIMULATION

Mainnet: NO
Real token: NO
Transferability: NO

SHA256 file: $ASSET.sha256
EOF

cat > "$OUT/RELEASE-NOTES.md" <<EOF
# AUNEYA v0.2.0

## Local Research Preview

Maintainer-operated release process.

### Verification

AUNEYA conformance checks passed: $COUNT

WVP Rust formatting: PASS

WVP Clippy: PASS

WVP tests: PASS

### Provenance

Source baseline: $BASE_SHA

Release commit: $RELEASE_SHA

### Independent review

External reviewer approval is not a release gate.

No independent audit is claimed.

### Limitations

This is a local research preview.

There is no production network,
real AUNEYA token, transferable asset,
real wallet or mainnet.

No market value is claimed.
EOF

echo
echo "========================================"
echo " PUBLISH GITHUB RELEASE"
echo "========================================"

git push origin "HEAD:refs/heads/$BRANCH"

git push origin "refs/tags/$TAG:refs/tags/$TAG"

REMOTE_SHA=$(
  git ls-remote origin "refs/tags/$TAG^{}" \
  | awk '{print $1}'
)

[ "$REMOTE_SHA" = "$RELEASE_SHA" ] || {
  echo "STOP: Remote-Tag SHA mismatch."
  exit 1
}

gh release create "$TAG" \
  --repo "$REPO" \
  --verify-tag \
  --title "AUNEYA v0.2.0 - Local Research Preview" \
  --notes-file "$OUT/RELEASE-NOTES.md" \
  --prerelease \
  --latest=false \
  "$OUT/$ASSET" \
  "$OUT/$ASSET.sha256" \
  "$OUT/AUNEYA-SELF-CHECK-v0.2.0.txt"

echo
echo "========================================"
echo " VERIFY PUBLISHED RELEASE"
echo "========================================"

gh release view "$TAG" \
  --repo "$REPO" \
  --json url,tagName,isPrerelease \
  --jq '"RELEASE: \(.url) | TAG: \(.tagName) | PREVIEW: \(.isPrerelease)"'

echo
echo "========================================"
echo " AUNEYA RELEASE COMPLETED"
echo "========================================"

printf 'Source SHA: %s\n' "$BASE_SHA"
printf 'Release SHA: %s\n' "$RELEASE_SHA"
printf 'Tests: %s AUNEYA conformance scripts\n' "$COUNT"
printf 'Prüfprotokoll: %s\n' "$OUT/self-check.log"
