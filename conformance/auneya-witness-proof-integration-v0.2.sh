#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests/auneya \
  -p 'test_witness_proof_integration.py' \
  -v
