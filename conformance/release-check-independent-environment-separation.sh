#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP INDEPENDENT-ENVIRONMENT SEPARATION CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/INDEPENDENT-ENVIRONMENT-EVIDENCE-SEPARATION.md"
SCRIPT="scripts/release/classify-build-environment.sh"

test -s "$DOC"
test -x "$SCRIPT"

grep -Fq "This is not a reproducible-build proof." "$DOC"
grep -Fq "This is not independent reproducibility evidence by itself." "$DOC"
grep -Fq "android-termux-aarch64" "$DOC"
grep -Fq "github-actions-linux-x86_64" "$DOC"
grep -Fq "reproducible_build_claim: false" "$DOC"
grep -Fq "Evidence from one environment class must not be treated as equivalent" "$DOC"

LOG="target/wvp-independent-environment-separation-$(date +%Y%m%d-%H%M%S).log"

"$SCRIPT" | tee "$LOG"

OUT_DIR="$(grep -F 'Artifact directory:' "$LOG" | tail -n 1 | sed 's/^Artifact directory: //')"

if [ -z "$OUT_DIR" ] || [ ! -d "$OUT_DIR" ]; then
  echo "FAIL: artifact directory not found"
  exit 1
fi

JSON="$OUT_DIR/BUILD-ENVIRONMENT-CLASSIFICATION.json"

test -s "$JSON"

grep -Fq '"evidence_type": "independent-environment-evidence-separation"' "$JSON"
grep -Fq '"reproducible_build_claim": false' "$JSON"
grep -Fq '"not_a_reproducible_build_proof": true' "$JSON"
grep -Fq '"independent_environment_evidence": false' "$JSON"
grep -Fq '"comparison_performed": false' "$JSON"
grep -Fq '"environment_class":' "$JSON"
grep -Fq '"cargo_lock_sha256":' "$JSON"
grep -Fq '"git_commit":' "$JSON"
grep -Fq '"rustc":' "$JSON"
grep -Fq '"cargo":' "$JSON"

ENV_CLASS="$(python3 - "$JSON" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)
print(data["environment_class"])
PY
)"

echo "Detected environment class: $ENV_CLASS"

case "$ENV_CLASS" in
  android-termux-aarch64|github-actions-linux-x86_64|linux-aarch64|linux-x86_64|unknown)
    ;;
  *)
    echo "FAIL: invalid environment class: $ENV_CLASS"
    exit 1
    ;;
esac

if [ "${GITHUB_ACTIONS:-false}" = "true" ]; then
  if [ "$ENV_CLASS" != "github-actions-linux-x86_64" ]; then
    echo "FAIL: expected github-actions-linux-x86_64 inside GitHub Actions, got $ENV_CLASS"
    exit 1
  fi
fi

if echo "$(uname -a)" | grep -qi 'Android'; then
  if [ "$ENV_CLASS" != "android-termux-aarch64" ]; then
    echo "FAIL: expected android-termux-aarch64 on Android/Termux, got $ENV_CLASS"
    exit 1
  fi
fi

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
