#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

PYTHONDONTWRITEBYTECODE=1 \
python3 tools/auneya/auneya_durable_delivery_v02.py self-test
