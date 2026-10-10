#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

PYTHONDONTWRITEBYTECODE=1 \
python3 tools/auneya/auneya_trusted_node_identity_v04.py self-test
