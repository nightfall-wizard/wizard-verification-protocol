# WVP Nightfall Release Download Verify v0.4

Generated UTC: `2026-10-05T14:54:21Z`

## Scope

This report verifies Nightfall release downloads against published SHA256 checksum files.

Repository checked:

- `Instinctes/nightfall`

Release:

- tag: `v1.0.5`
- name: `NIGHTFALLCOIN Core 1.0.5`
- published at: `2026-09-22T03:34:27Z`

This report is stacked after:

- `WVP Nightfall Release Asset Provenance v0.3`

## Safety boundary

No release binary is executed.

This check downloads files and computes SHA256 only.

## Download policy

| Field | Value |
|---|---:|
| Binary-like asset count | `8` |
| Checksum-like asset count | `3` |
| Total binary download size MB | `53` |
| Largest binary asset MB | `16` |
| Free storage MB | `23634` |
| Max total MB policy | `1200` |
| Max single asset MB policy | `450` |
| Size policy | `ok` |

## Verification summary

| Field | Value |
|---|---:|
| Pass count | `8` |
| Fail count | `0` |
| Missing checksum entry count | `0` |
| Skipped count | `0` |
| Verification verdict | `all_downloaded_binary_assets_match_published_sha256` |

## Passed SHA256 checks

```text
- nightfall-core-1.0.5-linux-x64 | pass | sha256=ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade
- nightfall-core-1.0.5-windows-x64.exe | pass | sha256=75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee
- nightfall-wallet-1.0.5-linux-x64 | pass | sha256=432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b
- nightfall-wallet-1.0.5-windows-x64.exe | pass | sha256=f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | pass | sha256=2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | pass | sha256=90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467
- nightfalld-1.0.5-linux-x64 | pass | sha256=b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236
- nightfalld-1.0.5-windows-x64.exe | pass | sha256=5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde
```

## Failed SHA256 checks

```text
- none
```

## Missing checksum entries

```text
- none
```

## Skipped

```text
- none
```

## Full verification table

```text
- nightfall-core-1.0.5-linux-x64 | pass | sha256=ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade
- nightfall-core-1.0.5-windows-x64.exe | pass | sha256=75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee
- nightfall-wallet-1.0.5-linux-x64 | pass | sha256=432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b
- nightfall-wallet-1.0.5-windows-x64.exe | pass | sha256=f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | pass | sha256=2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | pass | sha256=90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467
- nightfalld-1.0.5-linux-x64 | pass | sha256=b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236
- nightfalld-1.0.5-windows-x64.exe | pass | sha256=5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde
```

## Verdict

```text
published-checksum-files-present: yes
binary-assets-downloaded: yes
sha256-verification-result: all_downloaded_binary_assets_match_published_sha256
binary-execution-performed: no
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
```

## Interpretation

If SHA256 verification passes, it proves only that downloaded assets match the published checksum files.

It does not prove:

- that the checksum files are independently trustworthy;
- that the binaries match the source code;
- that the binaries were built by GitHub Actions;
- that the build is reproducible;
- that the binaries are safe;
- that the release is externally audited.

## Hard boundary

Checksum verification is an integrity check, not a security audit.

No binary safety claim is made.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-source-to-release-boundary-v0.5
```

It should check:

1. release tag commit;
2. workflow release configuration;
3. release asset names versus workflow asset names;
4. whether GitHub Actions can explain Linux/Windows assets;
5. whether macOS assets are manual or CI-built;
6. whether source-to-binary remains unproven.
