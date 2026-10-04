#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP BUILD ENVIRONMENT CLASSIFICATION ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

MANIFEST="reference/rust/wvp-release-check/Cargo.toml"

test -s "$MANIFEST"
test -s "Cargo.lock"

VERSION="$(grep -m1 '^version = ' "$MANIFEST" | sed -E 's/version = "([^"]+)"/\1/')"
COMMIT_SHA="$(git rev-parse HEAD)"
BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"
CARGO_LOCK_SHA256="$(sha256sum Cargo.lock | awk '{print $1}')"
RUSTC_VERSION="$(rustc --version)"
CARGO_VERSION="$(cargo --version)"
UNAME_VALUE="$(uname -a)"
UNAME_S="$(uname -s)"
UNAME_M="$(uname -m)"
GITHUB_ACTIONS_VALUE="${GITHUB_ACTIONS:-false}"
RUNNER_OS_VALUE="${RUNNER_OS:-unknown}"
TERMUX_VERSION_VALUE="${TERMUX_VERSION:-unknown}"
PREFIX_VALUE="${PREFIX:-unknown}"

DIRTY_STATE="false"
if [ -n "$(git status --porcelain)" ]; then
  DIRTY_STATE="true"
fi

ENV_CLASS="unknown"

# GitHub Actions is a CI evidence class and should be detected first.
if [ "$GITHUB_ACTIONS_VALUE" = "true" ] && [ "$RUNNER_OS_VALUE" = "Linux" ] && [ "$UNAME_M" = "x86_64" ]; then
  ENV_CLASS="github-actions-linux-x86_64"
fi

# Android/Termux often reports uname_s=Linux and uname_m=aarch64.
# Detect it by Android appearing anywhere in uname -a, Termux PREFIX,
# or TERMUX_VERSION. Do this before generic linux-aarch64 fallback.
if [ "$ENV_CLASS" = "unknown" ]; then
  if echo "$UNAME_VALUE" | grep -qi 'Android' && [ "$UNAME_M" = "aarch64" ]; then
    ENV_CLASS="android-termux-aarch64"
  fi
fi

if [ "$ENV_CLASS" = "unknown" ]; then
  if [ "$PREFIX_VALUE" = "/data/data/com.termux/files/usr" ] && [ "$UNAME_M" = "aarch64" ]; then
    ENV_CLASS="android-termux-aarch64"
  fi
fi

if [ "$ENV_CLASS" = "unknown" ]; then
  if [ "$TERMUX_VERSION_VALUE" != "unknown" ] && [ "$UNAME_M" = "aarch64" ]; then
    ENV_CLASS="android-termux-aarch64"
  fi
fi

if [ "$ENV_CLASS" = "unknown" ] && [ "$UNAME_S" = "Linux" ] && [ "$UNAME_M" = "aarch64" ]; then
  ENV_CLASS="linux-aarch64"
fi

if [ "$ENV_CLASS" = "unknown" ] && [ "$UNAME_S" = "Linux" ] && [ "$UNAME_M" = "x86_64" ]; then
  ENV_CLASS="linux-x86_64"
fi

OUT_DIR="target/wvp-environment-classification-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT_DIR"

JSON="$OUT_DIR/BUILD-ENVIRONMENT-CLASSIFICATION.json"

export WVP_ENV_TOOL="wvp-release-check"
export WVP_ENV_VERSION="$VERSION"
export WVP_ENV_COMMIT="$COMMIT_SHA"
export WVP_ENV_BRANCH="$BRANCH_NAME"
export WVP_ENV_DIRTY="$DIRTY_STATE"
export WVP_ENV_CARGO_LOCK_SHA256="$CARGO_LOCK_SHA256"
export WVP_ENV_RUSTC="$RUSTC_VERSION"
export WVP_ENV_CARGO="$CARGO_VERSION"
export WVP_ENV_UNAME="$UNAME_VALUE"
export WVP_ENV_UNAME_S="$UNAME_S"
export WVP_ENV_UNAME_M="$UNAME_M"
export WVP_ENV_GITHUB_ACTIONS="$GITHUB_ACTIONS_VALUE"
export WVP_ENV_RUNNER_OS="$RUNNER_OS_VALUE"
export WVP_ENV_TERMUX_VERSION="$TERMUX_VERSION_VALUE"
export WVP_ENV_PREFIX="$PREFIX_VALUE"
export WVP_ENV_CLASS="$ENV_CLASS"
export WVP_ENV_STARTED_AT="$START_TS"

python3 <<'PY' > "$JSON"
import json
import os

dirty = os.environ["WVP_ENV_DIRTY"] == "true"
github_actions = os.environ["WVP_ENV_GITHUB_ACTIONS"] == "true"

data = {
    "tool": os.environ["WVP_ENV_TOOL"],
    "package_version": os.environ["WVP_ENV_VERSION"],
    "evidence_type": "independent-environment-evidence-separation",
    "reproducible_build_claim": False,
    "not_a_reproducible_build_proof": True,
    "independent_environment_evidence": False,
    "comparison_performed": False,
    "environment_class": os.environ["WVP_ENV_CLASS"],
    "source": {
        "git_commit": os.environ["WVP_ENV_COMMIT"],
        "git_branch": os.environ["WVP_ENV_BRANCH"],
        "dirty": dirty,
    },
    "toolchain": {
        "rustc": os.environ["WVP_ENV_RUSTC"],
        "cargo": os.environ["WVP_ENV_CARGO"],
    },
    "inputs": {
        "cargo_lock_sha256": os.environ["WVP_ENV_CARGO_LOCK_SHA256"],
        "manifest": "reference/rust/wvp-release-check/Cargo.toml",
    },
    "environment": {
        "uname": os.environ["WVP_ENV_UNAME"],
        "uname_s": os.environ["WVP_ENV_UNAME_S"],
        "uname_m": os.environ["WVP_ENV_UNAME_M"],
        "github_actions": github_actions,
        "runner_os": os.environ["WVP_ENV_RUNNER_OS"],
        "termux_version": os.environ["WVP_ENV_TERMUX_VERSION"],
        "prefix": os.environ["WVP_ENV_PREFIX"],
    },
    "separation_rules": [
        "android-termux-aarch64 evidence must not be merged with github-actions-linux-x86_64 evidence without explicit comparison",
        "same-environment repeat-build evidence is not independent-environment evidence",
        "unknown environment evidence must not be used for strong reproducibility claims",
    ],
    "limitations": [
        "environment classification is not a reproducible-build proof",
        "environment classification does not prove binary safety",
        "environment classification does not prove source-build correspondence",
        "no independent binary comparison was performed by this script",
    ],
    "build": {
        "started_at": os.environ["WVP_ENV_STARTED_AT"],
    },
}

print(json.dumps(data, indent=2, sort_keys=True))
PY

echo "Environment class: $ENV_CLASS"
echo "Output directory: $OUT_DIR"
echo

echo "=== ENVIRONMENT CLASSIFICATION JSON ==="
cat "$JSON"
echo

case "$ENV_CLASS" in
  android-termux-aarch64|github-actions-linux-x86_64|linux-aarch64|linux-x86_64|unknown)
    ;;
  *)
    echo "FAIL: invalid environment class: $ENV_CLASS"
    exit 1
    ;;
esac

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Artifact directory: $OUT_DIR"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
