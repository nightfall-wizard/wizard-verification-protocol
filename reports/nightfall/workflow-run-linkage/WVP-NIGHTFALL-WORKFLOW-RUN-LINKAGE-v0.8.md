# WVP Nightfall Workflow Run Linkage v0.8

Generated UTC: `2026-10-05T15:17:38Z`

## Scope

This report checks whether Nightfall release assets can be linked to public GitHub Actions workflow runs and artifacts.

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

- `WVP Nightfall Build Attestation Gap v0.7`

## Safety boundary

No release binary is executed.

No local release build is performed.

This report checks public workflow-run metadata and artifact-name linkage only.

## Workflow-run linkage summary

| Field | Value |
|---|---:|
| Release asset count | `11` |
| Binary-like asset count | `8` |
| Checksum-like asset count | `3` |
| Signature-like asset count | `0` |
| Candidate workflow runs found | `2` |
| Workflow artifacts found | `0` |
| Expired workflow artifacts | `0` |
| Exact asset/artifact name matches | `0` |
| Category-surface matches | `0` |
| Assets without detected artifact linkage | `11` |
| Release-body workflow-run URL count | `0` |
| Linkage verdict | `candidate_runs_found_but_no_artifacts_found` |

## Candidate workflow runs

```text
- run_id=35646670905 | name=Release | event=push | status=completed | conclusion=success | head_branch=v1.0.5 | head_sha=9591ac0a3a58f734883f8b248b7b05aac88ee8f0 | created_at=2026-09-21T19:44:07Z | url=https://github.com/Instinctes/nightfall/actions/runs/35646670905
- run_id=35646590582 | name=CI | event=push | status=completed | conclusion=success | head_branch=main | head_sha=9591ac0a3a58f734883f8b248b7b05aac88ee8f0 | created_at=2026-09-21T19:43:19Z | url=https://github.com/Instinctes/nightfall/actions/runs/35646590582
```

## Workflow artifacts

```text
- none
```

## Asset-to-workflow artifact linkage

```text
- nightfall-core-1.0.5-linux-x64 | category=linux-binary | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- nightfall-core-1.0.5-windows-x64.exe | category=windows-binary | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- nightfall-wallet-1.0.5-linux-x64 | category=linux-binary | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- nightfall-wallet-1.0.5-windows-x64.exe | category=windows-binary | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | category=macos-artifact | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | category=macos-artifact | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- nightfalld-1.0.5-linux-x64 | category=linux-binary | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- nightfalld-1.0.5-windows-x64.exe | category=windows-binary | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- SHA256SUMS-1.0.5-linux.txt | category=checksum | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- SHA256SUMS-1.0.5-windows.txt | category=checksum | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
- SHA256SUMS-1.0.5.txt | category=checksum | linkage=no_workflow_artifact_link_detected | limitation=artifact-name-linkage-is-heuristic
```

## Verdict

```text
release-tag-commit-visible: yes
candidate-workflow-runs-found: yes
workflow-artifacts-found: no
exact-asset-artifact-name-linkage: 0/11
category-surface-linkage: 0/11
asset-workflow-linkage-result: candidate_runs_found_but_no_artifacts_found
binary-execution-performed: no
local-release-build-performed: no
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
```

## Interpretation

This v0.8 report checks whether release assets can be connected to public workflow-run and artifact metadata.

It does not prove:

- that release binaries match source;
- that release binaries were built by the detected workflow runs;
- that detected artifacts are identical to release assets;
- that macOS artifacts are CI-built;
- that builds are reproducible;
- that binaries are safe;
- that Nightfall is externally audited.

## Hard boundary

Workflow-run linkage is provenance evidence only.

Artifact-name linkage is heuristic unless artifact digests, release asset digests and workflow provenance all match.

No legal, custody or investment claim is made.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-slsa-provenance-gap-v0.9
```

It should check:

1. whether SLSA-style provenance exists;
2. whether provenance identifies builder identity;
3. whether provenance identifies source commit;
4. whether provenance links to release assets;
5. whether provenance is complete or partial;
6. whether source-to-binary remains unproven.
