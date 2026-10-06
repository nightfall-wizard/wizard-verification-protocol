
# WVP Post-Merge Operations

After merging a WVP evidence branch:

1. Confirm required checks passed.
2. Confirm branch protection remains active.
3. Re-run release-pack verification.
4. Tag or record the evidence pack state if appropriate.
5. Confirm public report remains sanitized.
6. Review PROJECT-STATE.md.
7. Open follow-up issue for the next milestone.

## Do not

- represent WVP as an audit
- claim project safety
- publish exploit-enabling details
- commit seeds, keys, wallet files, or live funds

## Maintenance cadence

Recommended cadence:

- run checks after every evidence change
- refresh public report after major updates
- refresh release pack before every review milestone
- review disclosure policy before publishing security-sensitive material
