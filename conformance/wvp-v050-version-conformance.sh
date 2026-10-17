#!/usr/bin/env bash
set -Eeuo pipefail
python3 - <<'INNERCHECK'
from pathlib import Path
import tomllib
with Path('reference/rust/wvp-release-check/Cargo.toml').open('rb') as fp:
    assert tomllib.load(fp)['package']['version'] == '0.5.0'
with Path('Cargo.lock').open('rb') as fp:
    packages = tomllib.load(fp)['package']
assert sum(p['name'] == 'wvp-release-check' and p['version'] == '0.5.0' for p in packages) == 1
assert Path('docs/release/WVP-V0.5.0-CANDIDATE.md').is_file()
assert Path('tools/wvp_bundle_verify_v050.py').is_file()
assert Path('tests/test_wvp_bundle_v050.py').is_file()
print('PASS: WVP v0.5 candidate package/lock/code/evidence identity')
INNERCHECK
