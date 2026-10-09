#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m unittest discover \
  -s tests/auneya \
  -p 'test_attestation_binding.py' \
  -v
