#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

PYTHONDONTWRITEBYTECODE=1 \
python3 tools/auneya/auneya_authenticated_ack_v03.py self-test
