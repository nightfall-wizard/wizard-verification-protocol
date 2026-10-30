#!/usr/bin/env bash
set -euo pipefail

python3 - <<'CHECK'
import tomllib
from pathlib import Path

with open('reference/rust/wvp-release-check/Cargo.toml', 'rb') as f:
    assert tuple(map(int,tomllib.load(f)['package']['version'].split('.'))) >= (0,4,0)

with open('reference/rust/wvp-release-check/Cargo.toml', 'rb') as f:
    current_version = tomllib.load(f)['package']['version']

with open('Cargo.lock', 'rb') as f:
    rows = tomllib.load(f)['package']

assert len([
    x for x in rows
    if x['name'] == 'wvp-release-check'
    and x['version'] == current_version
]) == 1

text = Path('README.md').read_text()

# Current public README wording; historical v0.4 preparation records remain.
# Do not assert that the release remains unpublished: this gate must also work
# after v0.4.0 is tagged. Publication state has a separate lifecycle CI gate.
start = '<!-- WVP:V040-PUBLIC-STATUS:START -->'
end = '<!-- WVP:V040-PUBLIC-STATUS:END -->'

assert text.count(start) == 1
assert text.count(end) == 1

block = text.split(start, 1)[1].split(end, 1)[0]

for required in (
    'HISTORICAL SNAPSHOT ONLY',
    'releases/tag/v0.4.0',
    'was published',
):
    assert required in block, required

assert 'v0.4.0 has not been released' not in block

assert 'independent security audit' in text
assert 'reproducible binary builds' in text


print('PASS: WVP v0.4 historical publication / current version lock and honest public status')
CHECK
