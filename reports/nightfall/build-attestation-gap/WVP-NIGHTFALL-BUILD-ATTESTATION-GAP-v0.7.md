# WVP Nightfall Build Attestation Gap v0.7

Generated UTC: `2026-10-05T15:11:38Z`

## Scope

This report checks whether Nightfall release assets have public build-attestation evidence.

Repository checked:

- `Instinctes/nightfall`

Release:

- tag: `v1.0.5`
- name: `NIGHTFALLCOIN Core 1.0.5`
- published at: `2026-09-22T03:34:27Z`
- release author: `Instinctes`

This report is stacked after:

- `WVP Nightfall Reproducibility Gap v0.6`

## Safety boundary

No release binary is executed.

Downloaded files are used only for metadata and attestation verification.

No local release build is performed.

## Asset and attestation summary

| Field | Value |
|---|---:|
| Release asset count | `11` |
| Binary-like asset count | `8` |
| Checksum-like asset count | `3` |
| Signature-like asset count | `0` |
| GitHub API asset digests present | `11` |
| GitHub API asset digests missing | `0` |
| gh attestation command available | `yes` |
| Total binary download size MB | `53` |
| Largest binary asset MB | `16` |
| Free storage MB | `23490` |
| Size policy | `ok` |
| Attestation pass count | `0` |
| Attestation fail count | `8` |
| Attestation skipped count | `0` |
| Attestation verdict | `no_binary_asset_attestation_verified` |

## GitHub Release Asset API digests

```text
- - nightfall-core-1.0.5-linux-x64 | api_digest=sha256:ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade | size=16325424 | uploader=github-actions[bot]
- - nightfall-core-1.0.5-windows-x64.exe | api_digest=sha256:75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee | size=9003008 | uploader=github-actions[bot]
- - nightfall-wallet-1.0.5-linux-x64 | api_digest=sha256:432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b | size=1710376 | uploader=github-actions[bot]
- - nightfall-wallet-1.0.5-windows-x64.exe | api_digest=sha256:f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183 | size=1231360 | uploader=github-actions[bot]
- - NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | api_digest=sha256:2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5 | size=8060841 | uploader=Instinctes
- - NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | api_digest=sha256:90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467 | size=9190889 | uploader=Instinctes
- - nightfalld-1.0.5-linux-x64 | api_digest=sha256:b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236 | size=5455656 | uploader=github-actions[bot]
- - nightfalld-1.0.5-windows-x64.exe | api_digest=sha256:5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde | size=4158976 | uploader=github-actions[bot]
- - SHA256SUMS-1.0.5-linux.txt | api_digest=sha256:0532425d650c3887ea8a5d5438345a149b4ad5a5a54410ab49419c6ce03d9ebc | size=289 | uploader=github-actions[bot]
- - SHA256SUMS-1.0.5-windows.txt | api_digest=sha256:1a84c6d019c66ae9ecbef3bf85345798241311d8f43674ef30b67b7182769991 | size=307 | uploader=github-actions[bot]
- - SHA256SUMS-1.0.5.txt | api_digest=sha256:88dcf695ff8ae5ee724347ced812779c7b4ec51f3ae0062624316c599d9f6a92 | size=214 | uploader=Instinctes
```

## Passed attestation checks

```text
- none
```

## Failed attestation checks

```text
- nightfall-core-1.0.5-linux-x64 | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-core-1.0.5-windows-x64.exe | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-linux-x64 | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-windows-x64.exe | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-linux-x64 | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-windows-x64.exe | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
```

## Skipped attestation checks

```text
- none
```

## Full attestation table

```text
- nightfall-core-1.0.5-linux-x64 | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-core-1.0.5-windows-x64.exe | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-linux-x64 | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-windows-x64.exe | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-linux-x64 | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-windows-x64.exe | fail | gh_attestation_not_verified |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
```

## Verdict

```text
github-release-asset-digests-present: yes
gh-attestation-cli-available: yes
binary-assets-downloaded-for-attestation-only: yes
attestation-verification-result: no_binary_asset_attestation_verified
binary-execution-performed: no
local-release-build-performed: no
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
```

## Interpretation

This v0.7 report checks whether public GitHub attestation evidence can be found and verified for release assets.

It does not prove:

- that release binaries match source;
- that binaries were built by the intended workflow;
- that every release asset is reproducible;
- that the build environment is fully pinned;
- that binaries are safe;
- that Nightfall is externally audited.

## Hard boundary

A verified attestation, if present, is provenance evidence.

It is not the same as a security audit.

It is not full source-to-binary proof unless it can be linked to the expected commit, workflow, builder identity and reproducible build process.

No legal, custody or investment claim is made.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-workflow-run-linkage-v0.8
```

It should check:

1. whether release assets can be linked to specific workflow runs;
2. whether workflow runs point to the release tag commit;
3. whether uploaded artifacts match release asset names;
4. whether macOS artifacts remain manually uploaded or CI-explained;
5. whether provenance evidence is complete or partial;
6. whether source-to-binary remains unproven.
