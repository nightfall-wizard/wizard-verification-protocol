# WVP v0.5.0 candidate — cryptographic evidence binding

## Actual scope

New offline verifier `tools/wvp_bundle_verify_v050.py` enforces a **single payload**
with two mandatory independent proof types, `PAYLOAD.sha256` and `PAYLOAD.sig`.
The manifest must contain exactly one GNU SHA256 record naming the *same* payload.
The detached RSA/SHA256 signature must verify that payload against a caller-selected
**trusted external public key**. All extra unsigned or ambiguous files are rejected.
The verifier reads untrusted release files without following symlinks, takes a
private snapshot and verifies the snapshot, not a mutable post-hash pathname.

## Local usage

```bash
python3 tools/wvp_bundle_verify_v050.py \
  --bundle /path/to/one-asset-release-bundle \
  --public-key keys/release/wvp-release-signing-public.pem
```

The bundle must contain exactly `artifact`, `artifact.sha256`, `artifact.sig`.
For multiple binaries verify **each separately** in its own bundle. A signature
is not meaningful until the public key is independently trusted.

## Adversarial regression suite

```bash
python3 -m unittest discover -s tests -p 'test_wvp_bundle_v050.py' -v
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --locked
```

Tested conditions include tampering with asset, manifest, signature, wrong key,
signature over another file, missing or duplicate evidence, extra unsigned files,
name confusion and symlinks.

## Release decision

This PR prepares the **source code** for v0.5.0; it does **not** publish a
GitHub Release, Git tag, Android binary or cryptographic claim about an
unsigned distribution. After the maintainer merges this PR and green CI is
observed, tag exactly that checked main commit and publish separately.

Only a release carrying a verifiable detached signature may claim successful
cryptographic signature checking. An unsigned source-only release must say so.
The historical v0.5-RC1 documents from October 7 remain historical evidence;
they do not prove this candidate passed its own new checks.

## Limits

This is **not an independent audit**, a proof that source equals binary,
a reproducible-build proof, a malware scan, wallet-safety verification,
or a guarantee of upstream protocol correctness. GitHub hosting alone does not
establish signer trust.
