#!/usr/bin/env bash
set -Eeuo pipefail

python3 - <<'CHECK'
import tomllib
from pathlib import Path

with Path(
    'reference/rust/wvp-release-check/Cargo.toml'
).open('rb') as fp:
    version = tomllib.load(fp)['package']['version']

assert tuple(
    map(int, version.split('.'))
) >= (0, 5, 0)

with Path('Cargo.lock').open('rb') as fp:
    packages = tomllib.load(fp)['package']

assert sum(
    item['name'] == 'wvp-release-check'
    and item['version'] == version
    for item in packages
) == 1

for filename in [
    'docs/release/WVP-V0.5.0-CANDIDATE.md',
    'tools/wvp_bundle_verify_v050.py',
    'tests/test_wvp_bundle_v050.py',
]:
    assert Path(filename).is_file(), filename

print(
    'PASS: WVP version identity and historical evidence'
)
CHECK
