# WVP Nightfall Release Check v0.2

Generated UTC: `2026-10-05T14:48:10Z`

## Scope

This report checks public GitHub release metadata for Nightfall.

Repository checked:

- `Instinctes/nightfall`

This report is stacked after:

- `WVP Nightfall Reality Report v0.1`

## Latest release API status

| Field | Value |
|---|---:|
| Latest release found | `yes` |
| Tag | `v1.0.5` |
| Name | `NIGHTFALLCOIN Core 1.0.5` |
| Draft | `false` |
| Prerelease | `false` |
| Published at | `2026-09-22T03:34:27Z` |
| Release author | `Instinctes` |
| Asset count | `11` |
| Checksum-like assets | `3` |
| Signature-like assets | `0` |

## Release assets

```text
- nightfall-core-1.0.5-linux-x64
- nightfall-core-1.0.5-windows-x64.exe
- nightfall-wallet-1.0.5-linux-x64
- nightfall-wallet-1.0.5-windows-x64.exe
- NIGHTFALLCOIN-Core-1.0.5-macOS-arm64.dmg
- NIGHTFALLCOIN-Core-1.0.5-macOS-intel.dmg
- nightfalld-1.0.5-linux-x64
- nightfalld-1.0.5-windows-x64.exe
- SHA256SUMS-1.0.5-linux.txt
- SHA256SUMS-1.0.5-windows.txt
- SHA256SUMS-1.0.5.txt
```

## Verdict

```text
release-api-inspectable: yes
release-assets-present: yes
checksum-assets-detected: yes
signature-assets-detected: no
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
```

## Interpretation

This v0.2 check only verifies GitHub release metadata and release asset naming.

It does not prove:

- that release binaries are safe;
- that release binaries match the source code;
- that builds are reproducible;
- that the release was independently audited;
- that checksums, if present, are independently trustworthy;
- that signatures, if present, are tied to a verified maintainer identity.

## Hard boundary

A release can have assets, checksums and signatures and still not be security-proven.

WVP must not treat release metadata as audit evidence.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-release-asset-provenance-v0.3
```

It should check:

1. asset uploader identity;
2. GitHub Actions artifact link if available;
3. tag commit;
4. release commit;
5. whether source archive matches tag;
6. whether checksums cover every binary asset;
7. whether signatures can be verified against a published public key.
