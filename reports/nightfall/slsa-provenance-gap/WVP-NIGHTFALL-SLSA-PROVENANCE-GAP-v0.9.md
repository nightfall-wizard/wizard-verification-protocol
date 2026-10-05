# WVP Nightfall SLSA Provenance Gap v0.9

Generated UTC: `2026-10-05T15:38:03Z`

## Scope

This report checks whether Nightfall release binary-like assets have usable SLSA/in-toto provenance surface.

Repository checked:

- `Instinctes/nightfall`

Release:

- tag: `v1.0.5`
- name: `NIGHTFALLCOIN Core 1.0.5`
- published at: `2026-09-22T03:34:27Z`
- release author: `Instinctes`
- target commitish: `main`
- tag commit SHA: `9591ac0a3a58f734883f8b248b7b05aac88ee8f0`

This report is stacked after:

- `WVP Nightfall Workflow Run Linkage v0.8`

## Safety boundary

No release binary is executed.

Downloaded files are used only for SHA256 digest calculation and GitHub attestation/provenance verification.

No local release build is performed.

## SLSA / provenance summary

| Field | Value |
|---|---:|
| Release asset count | `11` |
| Binary-like asset count | `8` |
| Checksum-like asset count | `3` |
| Signature-like asset count | `0` |
| gh attestation command available | `yes` |
| Total binary download size MB | `53` |
| Largest binary asset MB | `16` |
| Free storage MB | `23469` |
| Size policy | `ok` |
| Strong SLSA surface count | `0` |
| Partial provenance surface count | `0` |
| Provenance fail count | `8` |
| Provenance skipped count | `0` |
| SLSA verdict | `no_slsa_provenance_surface_verified` |

## Strong SLSA surface

```text
- none
```

## Partial provenance surface

```text
- none
```

## Failed provenance checks

```text
- nightfall-core-1.0.5-linux-x64 | fail | no_verified_attestation | local_sha256=ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-core-1.0.5-windows-x64.exe | fail | no_verified_attestation | local_sha256=75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-linux-x64 | fail | no_verified_attestation | local_sha256=432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-windows-x64.exe | fail | no_verified_attestation | local_sha256=f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | fail | no_verified_attestation | local_sha256=2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | fail | no_verified_attestation | local_sha256=90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-linux-x64 | fail | no_verified_attestation | local_sha256=b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-windows-x64.exe | fail | no_verified_attestation | local_sha256=5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
```

## Skipped provenance checks

```text
- none
```

## Full provenance table

```text
- nightfall-core-1.0.5-linux-x64 | fail | no_verified_attestation | local_sha256=ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:ed5136eca5769654ee103b1e2061037787494da1aa96371b85cb90d2bd1fcade?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-core-1.0.5-windows-x64.exe | fail | no_verified_attestation | local_sha256=75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:75c8f7ca8487b3c086e1efd94e8469b17b1b79b7cdd37429bd4f4b3e98e605ee?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-linux-x64 | fail | no_verified_attestation | local_sha256=432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:432fba1360f563a72853b83e0124da1713fdf551bbfdd28954a68d422dad8c3b?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfall-wallet-1.0.5-windows-x64.exe | fail | no_verified_attestation | local_sha256=f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:f4d06a799c8e0082fead6bf17e76370b8a3345e7912d985d325c6a7db93a9183?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | fail | no_verified_attestation | local_sha256=2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:2f05818ca6d91cce54a73e882b0ffbcb0c7476cf87343da1b3a973c676027de5?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | fail | no_verified_attestation | local_sha256=90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:90a55ea773c7887210e1b79b8515d42e19a10316c45ba31d6180fed8ecf57467?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-linux-x64 | fail | no_verified_attestation | local_sha256=b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236 |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:b5b623adefecc48de0c5e361650736c93d320c53a1be53189f21f005f5317236?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
- nightfalld-1.0.5-windows-x64.exe | fail | no_verified_attestation | local_sha256=5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde |  Error: HTTP 404: Not Found (https://api.github.com/repos/Instinctes/nightfall/attestations/sha256:5acd1825e717a705d57c42cf62cdba473bc1746e5211737fa967ccbe2099dfde?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprov
```

## Verdict

```text
release-tag-commit-visible: yes
gh-attestation-cli-available: yes
binary-assets-downloaded-for-provenance-only: yes
slsa-provenance-result: no_slsa_provenance_surface_verified
binary-execution-performed: no
local-release-build-performed: no
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
```

## Interpretation

This v0.9 report checks whether release assets expose usable provenance surface.

It checks for signals such as:

- in-toto statement surface;
- SLSA provenance surface;
- builder identity surface;
- subject/digest surface;
- release tag commit linkage;
- repository linkage;
- workflow linkage.

It does not prove:

- that release binaries match source;
- that the release assets are byte-identical to workflow artifacts;
- that builds are reproducible;
- that binaries are safe;
- that Nightfall is externally audited.

## Hard boundary

SLSA/in-toto provenance, if present, is provenance evidence.

It is not a security audit.

It is not a full source-to-binary proof unless the provenance links the expected source commit, builder identity, workflow, subject digest, release asset digest and reproducible build process.

No legal, custody or investment claim is made.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-final-reality-verdict-v1.0
```

It should consolidate:

1. v0.1 claim matrix;
2. v0.2 release metadata;
3. v0.3 asset provenance;
4. v0.4 checksum verification;
5. v0.5 source-to-release boundary;
6. v0.6 reproducibility gap;
7. v0.7 build attestation gap;
8. v0.8 workflow-run linkage;
9. v0.9 SLSA provenance gap;
10. final non-claim boundary.
