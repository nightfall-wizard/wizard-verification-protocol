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

# Current public README wording; historical v0.4 preparation records remain.
# Do not assert that the release remains unpublished: this gate must also work
# after v0.4.0 is tagged. Publication state has a separate lifecycle CI gate.
assert '## WVP v0.4 Public Status' in text
assert 'This is not an audit.' in text
assert 'This is not a source-to-release proof.' in text

print('PASS: WVP v0.4 source version + lock + honest public status')
CHECK
