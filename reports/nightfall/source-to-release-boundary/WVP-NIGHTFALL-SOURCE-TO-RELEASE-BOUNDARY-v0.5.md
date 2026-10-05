# WVP Nightfall Source-to-Release Boundary v0.5

Generated UTC: `2026-10-05T15:05:36Z`

## Scope

This report checks the boundary between Nightfall source tags, release workflow surface and published GitHub release assets.

Repository checked:

- `Instinctes/nightfall`

Release:

- tag: `v1.0.5`
- name: `NIGHTFALLCOIN Core 1.0.5`
- published at: `2026-09-22T03:34:27Z`
- release author: `Instinctes`
- target commitish: `main`

This report is stacked after:

- `WVP Nightfall Release Download Verify v0.4`

## Source and workflow evidence

| Field | Value |
|---|---:|
| Tag found | `yes` |
| Tag ref SHA | `9591ac0a3a58f734883f8b248b7b05aac88ee8f0` |
| Tag peeled SHA | `` |
| Tag local commit SHA | `9591ac0a3a58f734883f8b248b7b05aac88ee8f0` |
| Release workflow present at tag | `yes` |
| Workflow mentions Linux surface | `yes` |
| Workflow mentions Windows surface | `yes` |
| Workflow mentions macOS surface | `yes` |
| Workflow mentions checksum surface | `yes` |
| Workflow mentions release upload surface | `yes` |
| Release asset count | `11` |
| Assets with workflow surface explanation | `11` |
| Assets not explained by simple workflow surface | `0` |
| Release-note safety keyword count | `0` |

## Asset boundary table

```text
- nightfall-core-1.0.5-linux-x64 | category=linux-binary | workflow_surface=workflow_mentions_linux_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- nightfall-core-1.0.5-windows-x64.exe | category=windows-binary | workflow_surface=workflow_mentions_windows_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- nightfall-wallet-1.0.5-linux-x64 | category=linux-binary | workflow_surface=workflow_mentions_linux_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- nightfall-wallet-1.0.5-windows-x64.exe | category=windows-binary | workflow_surface=workflow_mentions_windows_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | category=macos-artifact | workflow_surface=workflow_mentions_macos_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | category=macos-artifact | workflow_surface=workflow_mentions_macos_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- nightfalld-1.0.5-linux-x64 | category=linux-binary | workflow_surface=workflow_mentions_linux_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- nightfalld-1.0.5-windows-x64.exe | category=windows-binary | workflow_surface=workflow_mentions_windows_and_release_upload_surface | limitation=heuristic_filename_and_workflow_surface_only
- SHA256SUMS-1.0.5-linux.txt | category=checksum | workflow_surface=workflow_mentions_checksum_generation_or_upload | limitation=heuristic_filename_and_workflow_surface_only
- SHA256SUMS-1.0.5-windows.txt | category=checksum | workflow_surface=workflow_mentions_checksum_generation_or_upload | limitation=heuristic_filename_and_workflow_surface_only
- SHA256SUMS-1.0.5.txt | category=checksum | workflow_surface=workflow_mentions_checksum_generation_or_upload | limitation=heuristic_filename_and_workflow_surface_only
```

## Verdict

```text
release-tag-visible: yes
release-workflow-present-at-tag: yes
linux-assets-workflow-surface: yes
windows-assets-workflow-surface: yes
macos-assets-workflow-surface: yes
checksum-assets-workflow-surface: yes
release-upload-workflow-surface: yes
source-to-release-boundary-inspectable: yes
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
```

## Interpretation

This v0.5 report checks whether release assets are explainable by public source-tag and workflow surface evidence.

It does not prove:

- that release binaries match source;
- that binaries were built by GitHub Actions;
- that macOS artifacts were CI-built;
- that builds are reproducible;
- that the binaries are safe;
- that checksum files are independently trustworthy;
- that Nightfall is externally audited.

## Hard boundary

Workflow surface evidence is not source-to-binary proof.

A release workflow can explain intended build paths, but WVP must not treat that as reproducibility or binary safety evidence.

No binary execution is performed.

No legal, custody or investment claim is made.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-reproducibility-gap-v0.6
```

It should check:

1. whether build instructions are complete;
2. whether exact toolchain versions are pinned;
3. whether Cargo.lock exists and is release-bound;
4. whether GitHub Actions build environment is pinned enough;
5. whether local Android/Termux can reproduce metadata only;
6. whether byte-identical reproducible builds remain unproven.
