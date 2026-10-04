# WVP v0.2 Release Build Procedure

## Status

This document describes the local WVP v0.2 release build procedure.

This does not create a release by itself.

This does not create a tag.

This does not upload assets.

## Version

The release candidate version is:

- `0.2.0`

## Local build script

The local release build script is:

- `scripts/release/build-wvp-release-check-v020.sh`

## What the script does

The script performs:

1. verifies `wvp-release-check` is at version `0.2.0`
2. verifies the private signing key exists outside the repository
3. builds the release binary
4. copies the binary into a timestamped target directory
5. checks that the binary reports version `0.2.0`
6. creates a `.sha256` checksum asset
7. verifies the checksum locally
8. creates a detached `.sig` signature asset
9. verifies the detached signature locally
10. prints the local artifact directory

## What the script does not do

The script does not create a Git tag.

The script does not create a GitHub release.

The script does not upload assets.

The script does not commit files.

The script does not push to GitHub.

## Expected local artifacts

The build produces:

- `wvp-release-check-termux-android-aarch64`
- `wvp-release-check-termux-android-aarch64.sha256`
- `wvp-release-check-termux-android-aarch64.sig`

## Safety

The private signing key must remain outside the repository.

Only public verification material may be committed.

The generated release artifacts stay under `target/` unless explicitly uploaded in a later controlled step.
