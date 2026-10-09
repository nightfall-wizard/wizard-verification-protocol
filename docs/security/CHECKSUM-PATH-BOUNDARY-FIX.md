# Checksum artifact path boundary fix

## Problem and scope

WVP-INV-002 already requires path containment. Previously, the negative
fixture test inspected JSON fields but did not call production verification.
The production checksum path passed remote manifest bytes to sha256sum -c.
A manifest could name an existing file outside the downloaded artifact directory.

## Change and compatibility

The production checksum wrapper now calls an offline directory verifier.
It parses the complete manifest before reading listed assets, accepts SHA256
GNU text or binary records with flat filenames, rejects paths, control bytes,
duplicate names and self references, and rejects symlinks and nonregular files.
Manifest input is limited to 1 MiB. The hash process receives an opened file on
stdin; it never interprets an untrusted path or checksum manifest.
Linux/Android opens use O_NOFOLLOW and O_NONBLOCK; Unix inode/device identity
is checked after opening. No new dependency or lockfile change is needed.

This intentionally rejects nested paths, ./ prefixes, Windows paths,
GNU escaped filenames, empty records and unsupported checksum formats.
Existing flat SHA256 text/binary records remain supported. The change is not
part of the immutable RC1 tag; it requires a subsequent release to ship.

## Measured regression evidence

The existing FRC-SEC-002 artifact name is reused with the correct SHA256 of
a synthetic outside file. Digest mismatch cannot mask the path regression.
The previous sha256sum -c algorithm is first extracted without changing its
accept/reject behavior: valid input passes while traversal, absolute-path and
symlink rejection tests fail. The corrected implementation passes the suite.
Disabling only the artifact name guard causes the traversal test to fail again.
The script then restores the guard and runs all Rust tests, Clippy, formatting,
the Python suite and the existing release quality gate before publication.

## Reproduce

```sh
cargo test --locked -p wvp-release-check --test checksum_path_boundary
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
bash tools/check_release_quality_gate.sh
```

## Limits

The caller must control the artifact directory and its ancestors. This change
does not defend against a hostile process with the same OS account modifying
open files or directory ancestors. Linux/Android are the execution targets
for this change; cross-platform validation is not claimed. This is checksum
path containment, not full manifest coverage, signature-to-artifact binding,
binary safety, an independent audit or completion of WVP.
The structured evidence records local results only; remote CI is observed
separately after the commit. Unpublished local logs remain in the work folder.
