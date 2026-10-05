# WVP Nightfall Release Asset Provenance v0.3

Generated UTC: `2026-10-05T14:51:43Z`

## Scope

This report checks public GitHub release asset provenance signals for Nightfall.

Repository checked:

- `Instinctes/nightfall`

This report is stacked after:

- `WVP Nightfall Release Check v0.2`

## Latest release

| Field | Value |
|---|---:|
| Tag | `v1.0.5` |
| Name | `NIGHTFALLCOIN Core 1.0.5` |
| Target commitish | `main` |
| Release author | `Instinctes` |
| Published at | `2026-09-22T03:34:27Z` |
| Asset count | `11` |
| Binary-like assets | `8` |
| Checksum-like assets | `3` |
| Signature-like assets | `0` |
| Unique asset uploaders | `2` |
| Asset uploaders | `Instinctes, github-actions[bot]` |
| Tag found by git ls-remote | `yes` |
| Tag ref SHA | `9591ac0a3a58f734883f8b248b7b05aac88ee8f0` |
| Checksum coverage by filename | `complete_by_filename` |
| Binary assets covered by checksum filename match | `8` |
| Binary assets missing checksum filename match | `0` |

## Asset uploaders

```text
- nightfall-core-1.0.5-linux-x64 | uploader=github-actions[bot] | size=16325424 | downloads=8
- nightfall-core-1.0.5-windows-x64.exe | uploader=github-actions[bot] | size=9003008 | downloads=5
- nightfall-wallet-1.0.5-linux-x64 | uploader=github-actions[bot] | size=1710376 | downloads=6
- nightfall-wallet-1.0.5-windows-x64.exe | uploader=github-actions[bot] | size=1231360 | downloads=2
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg | uploader=Instinctes | size=8060841 | downloads=0
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg | uploader=Instinctes | size=9190889 | downloads=0
- nightfalld-1.0.5-linux-x64 | uploader=github-actions[bot] | size=5455656 | downloads=4
- nightfalld-1.0.5-windows-x64.exe | uploader=github-actions[bot] | size=4158976 | downloads=2
- SHA256SUMS-1.0.5-linux.txt | uploader=github-actions[bot] | size=289 | downloads=2
- SHA256SUMS-1.0.5-windows.txt | uploader=github-actions[bot] | size=307 | downloads=3
- SHA256SUMS-1.0.5.txt | uploader=Instinctes | size=214 | downloads=1
```

## Binary-like assets

```text
- nightfall-core-1.0.5-linux-x64
- nightfall-core-1.0.5-windows-x64.exe
- nightfall-wallet-1.0.5-linux-x64
- nightfall-wallet-1.0.5-windows-x64.exe
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg
- nightfalld-1.0.5-linux-x64
- nightfalld-1.0.5-windows-x64.exe
```

## Checksum-like assets

```text
- SHA256SUMS-1.0.5-linux.txt
- SHA256SUMS-1.0.5-windows.txt
- SHA256SUMS-1.0.5.txt
```

## Signature-like assets

```text
- none
```

## Binary assets covered by checksum filename match

```text
- nightfall-core-1.0.5-linux-x64
- nightfall-core-1.0.5-windows-x64.exe
- nightfall-wallet-1.0.5-linux-x64
- nightfall-wallet-1.0.5-windows-x64.exe
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg
- nightfalld-1.0.5-linux-x64
- nightfalld-1.0.5-windows-x64.exe
```

## Binary assets missing checksum filename match

```text
- none
```

## Verdict

```text
release-tag-found: yes
release-assets-present: yes
single-uploader-or-multiple-known-uploaders: inspectable
checksum-assets-present: yes
signature-assets-present: no
checksum-coverage-by-filename: complete_by_filename
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
maintainer-key-identity-proven: no
```

## Interpretation

This v0.3 report improves release evidence by checking:

- public release metadata;
- release tag visibility;
- asset uploader identity from GitHub metadata;
- checksum-like asset presence;
- signature-like asset presence;
- filename-level checksum coverage.

It does not prove:

- that the binaries are safe;
- that binaries were built by GitHub Actions;
- that the binaries match source;
- that the release is reproducible;
- that checksums are independently trustworthy;
- that uploader identity equals cryptographic maintainer identity;
- that Nightfall is externally audited.

## Hard boundary

Checksum files improve integrity checking, but they do not prove release trust by themselves.

Unsigned release assets remain weaker than signed assets.

No binary safety claim is made.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-release-download-verify-v0.4
```

It should verify:

1. download checksum files;
2. download small selected release assets only if safe and necessary;
3. compute SHA256 locally;
4. compare SHA256 values against published checksum files;
5. keep binary execution out of scope;
6. keep security/audit claims out of scope.
