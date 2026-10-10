#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHONDONTWRITEBYTECODE=1 \
python3 tools/auneya/auneya_two_node_research.py self-test
