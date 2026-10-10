#!/usr/bin/env bash
set -euo pipefail

python3 - <<'CHECK'
import tomllib
from pathlib import Path

with open('reference/rust/wvp-release-check/Cargo.toml', 'rb') as f:
    assert tomllib.load(f)['package']['version'] == '0.4.0'

with open('Cargo.lock', 'rb') as f:
    rows = tomllib.load(f)['package']

assert len([
    x for x in rows
    if x['name'] == 'wvp-release-check'
    and x['version'] == '0.4.0'
]) == 1

text = Path('README.md').read_text()

assert '## WVP v0.4 Release Track' in text
assert 'not independently audited' in text

print('PASS: WVP v0.4 source version + lock + honest public status')
CHECK
