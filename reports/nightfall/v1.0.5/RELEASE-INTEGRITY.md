# WVP-SEC-005 - Release Integrity Evidence

This report captures local release-integrity evidence for Nightfall.

Boundary: this is not an audit and does not prove binary provenance.

Evidence checks: 10
PASS: 10
WARN: 0

## Evidence summary

| ID | Name | Class | Status | Return code |
|---|---|---|---|---:|
| NF-REL-001 | `nightfall_repo_exists` | repository | `PASS` | 0 |
| NF-REL-002 | `nightfall_git_head` | source_identity | `PASS` | 0 |
| NF-REL-003 | `nightfall_remote` | source_identity | `PASS` | 0 |
| NF-REL-004 | `nightfall_tags` | release_identity | `PASS` | 0 |
| NF-REL-005 | `release_workflow_exists` | release_pipeline | `PASS` | 0 |
| NF-REL-006 | `ci_workflow_exists` | release_pipeline | `PASS` | 0 |
| NF-REL-007 | `cargo_lock_exists` | dependency_lock | `PASS` | 0 |
| NF-REL-008 | `cargo_toml_exists` | dependency_manifest | `PASS` | 0 |
| NF-REL-009 | `release_digest_terms` | artifact_integrity | `PASS` | 0 |
| NF-REL-010 | `release_security_terms` | security_boundary | `PASS` | 0 |

## File hashes

| Path | Exists | SHA-256 |
|---|---:|---|
| `/data/data/com.termux/files/home/nightfall/Cargo.lock` | `True` | `f95730fdfeec1e1651aeba5fc0017aff3443dc206ffd0f94fd4ba08dc1d82014` |
| `/data/data/com.termux/files/home/nightfall/Cargo.toml` | `True` | `14e217eaad55ba2391d7bde5679aee790a6c7be9086c43429f895e379145d46e` |
| `/data/data/com.termux/files/home/nightfall/.github/workflows/release.yml` | `True` | `de50ec13078be569b1682e185815b4f8875fe48c2c799297ece227c01ac8def4` |
| `/data/data/com.termux/files/home/nightfall/.github/workflows/ci.yml` | `True` | `e2eb7a7b21c672be4cfbeb8fb84c9ca3cf0cc82ff900ee6e93de4fd541d1bac9` |
| `/data/data/com.termux/files/home/nightfall/SECURITY.md` | `True` | `70fb360d2cb8f387670818591858abd81ccf90e7f1e2f6775111641c59e4368b` |
| `/data/data/com.termux/files/home/nightfall/docs/SPEC.md` | `True` | `97e757ec526baed68d87cd4649c4ee0cb1fd32e829a72283688a2002f177550b` |

## NF-REL-001 - nightfall_repo_exists

Status: `PASS`

Class: `repository`

Command:

```bash
test -d "$HOME/nightfall"
```

Stdout:

```text

```

## NF-REL-002 - nightfall_git_head

Status: `PASS`

Class: `source_identity`

Command:

```bash
git rev-parse HEAD
```

Stdout:

```text
f477b69f189054f09cbef84d6ac6c2ec5e36ff3c

```

## NF-REL-003 - nightfall_remote

Status: `PASS`

Class: `source_identity`

Command:

```bash
git remote -v
```

Stdout:

```text
canonical	https://github.com/Instinctes/nightfall.git (fetch)
canonical	https://github.com/Instinctes/nightfall.git (push)
fork	https://github.com/nightfall-wizard/nightfall.git (fetch)
fork	https://github.com/nightfall-wizard/nightfall.git (push)
origin	https://github.com/Instinctes/nightfall.git (fetch)
origin	https://github.com/Instinctes/nightfall.git (push)
realfork	https://github.com/nightfall-wizard/nightfall-wizard-fork.git (fetch)
realfork	https://github.com/nightfall-wizard/nightfall-wizard-fork.git (push)
upstream	https://github.com/Instinctes/nightfall.git (fetch)
upstream	https://github.com/Instinctes/nightfall.git (push)
wizard	https://github.com/nightfall-wizard/nightfall-wizard-fork.git (fetch)
wizard	https://github.com/nightfall-wizard/nightfall-wizard-fork.git (push)
wizard-fork	https://github.com/nightfall-wizard/nightfall-wizard-fork.git (fetch)
wizard-fork	https://github.com/nightfall-wizard/nightfall-wizard-fork.git (push)

```

## NF-REL-004 - nightfall_tags

Status: `PASS`

Class: `release_identity`

Command:

```bash
git tag --list | tail -30
```

Stdout:

```text
v0.5.4
v0.6.0
v0.6.1
v0.6.2
v0.6.3
v0.7.0
v0.7.1
v0.7.2
v0.7.3
v0.7.4
v0.7.5
v0.7.6
v0.7.7
v0.7.8
v0.8.0
v0.8.1
v0.8.2
v0.8.3
v0.8.4
v0.9.0
v0.9.1
v0.9.2
v0.9.4
v0.9.5
v1.0.0
v1.0.1
v1.0.2
v1.0.3
v1.0.4
v1.0.5

```

## NF-REL-005 - release_workflow_exists

Status: `PASS`

Class: `release_pipeline`

Command:

```bash
test -f .github/workflows/release.yml
```

Stdout:

```text

```

## NF-REL-006 - ci_workflow_exists

Status: `PASS`

Class: `release_pipeline`

Command:

```bash
test -f .github/workflows/ci.yml
```

Stdout:

```text

```

## NF-REL-007 - cargo_lock_exists

Status: `PASS`

Class: `dependency_lock`

Command:

```bash
test -f Cargo.lock
```

Stdout:

```text

```

## NF-REL-008 - cargo_toml_exists

Status: `PASS`

Class: `dependency_manifest`

Command:

```bash
test -f Cargo.toml
```

Stdout:

```text

```

## NF-REL-009 - release_digest_terms

Status: `PASS`

Class: `artifact_integrity`

Command:

```bash
grep -RniE 'sha256|digest|checksum|hash|artifact|release' .github docs RELEASE-NOTES 2>/dev/null | head -120
```

Stdout:

```text
.github/workflows/ci.yml:62:      # release-channels.mjs, which reads website/public/releases.json. The
.github/workflows/ci.yml:99:      - name: Build release binaries
.github/workflows/ci.yml:100:        run: cargo build --release -p nightfall-node -p nightfall-wallet -p nightfall-core
.github/workflows/release.yml:1:name: Release
.github/workflows/release.yml:4:# them to the release for the tag that triggered this.
.github/workflows/release.yml:45:      # The tests gate the release. Shipping a binary from a tree that fails
.github/workflows/release.yml:51:        run: cargo build --release -p nightfall-core -p nightfall-node -p nightfall-wallet
.github/workflows/release.yml:58:          $got = (& ./target/release/nightfalld.exe --version).Split(' ')[1]
.github/workflows/release.yml:67:      - name: Collect and checksum
.github/workflows/release.yml:76:          # binary under a new build's published checksum.
.github/workflows/release.yml:83:            Copy-Item "target/release/$src" "dist/$($map[$src])"
.github/workflows/release.yml:87:            "$((Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower())  $($_.Name)"
.github/workflows/release.yml:102:            (Join-Path $PWD "dist/SHA256SUMS-$version-windows.txt"),
.github/workflows/release.yml:106:          Get-Content "dist/SHA256SUMS-$version-windows.txt"
.github/workflows/release.yml:110:          # It then writes SHA256SUMS-main-windows.txt while every later step
.github/workflows/release.yml:111:          # looks for SHA256SUMS-<version>-windows.txt, and the run dies on a
.github/workflows/release.yml:117:      - name: The checksum list must be readable off Windows
.github/workflows/release.yml:122:          $path = "dist/SHA256SUMS-$version-windows.txt"
.github/workflows/release.yml:132:      - name: Attach to release
.github/workflows/release.yml:136:          # `gh release upload` needs a release, and pushing a tag does not
.github/workflows/release.yml:138:          # failed on this line because the release did not exist yet —
.github/workflows/release.yml:141:          # cannot invent a release for a commit nobody tagged.
.github/workflows/release.yml:142:          RELEASE_FLAGS=()
.github/workflows/release.yml:143:          if [[ "$TAG" == *-* ]]; then RELEASE_FLAGS=(--prerelease --latest=false); fi
.github/workflows/release.yml:144:          if ! gh release view "$TAG" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then
.github/workflows/release.yml:145:            gh release create "$TAG" --repo "$GITHUB_REPOSITORY" --verify-tag "${RELEASE_FLAGS[@]}" \
.github/workflows/release.yml:147:              --notes "Binaries built by this workflow. Verify the SHA256 before running anything."
.github/workflows/release.yml:150:          gh release upload "$TAG" dist/* --clobber --repo "$GITHUB_REPOSITORY"
.github/workflows/release.yml:176:        run: cargo build --release -p nightfall-core -p nightfall-node -p nightfall-wallet
.github/workflows/release.yml:186:          GOT="$(./target/release/nightfalld --version | awk '{print $2}')"
.github/workflows/release.yml:195:      - name: Collect and checksum
.github/workflows/release.yml:200:          cp target/release/nightfall-core "dist/nightfall-core-${VERSION}-linux-x64"
.github/workflows/release.yml:201:          cp target/release/nightfalld "dist/nightfalld-${VERSION}-linux-x64"
.github/workflows/release.yml:202:          cp target/release/nightfall-wallet "dist/nightfall-wallet-${VERSION}-linux-x64"
.github/workflows/release.yml:204:          (cd dist && sha256sum nightfall*-linux-x64 > "SHA256SUMS-${VERSION}-linux.txt")
.github/workflows/release.yml:205:          cat "dist/SHA256SUMS-${VERSION}-linux.txt"
.github/workflows/release.yml:209:      - name: Attach to release
.github/workflows/release.yml:213:          # of the two finishes first creates the release; the other finds it.
.github/workflows/release.yml:214:          RELEASE_FLAGS=()
.github/workflows/release.yml:215:          if [[ "$TAG" == *-* ]]; then RELEASE_FLAGS=(--prerelease --latest=false); fi
.github/workflows/release.yml:216:          if ! gh release view "$TAG" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then
.github/workflows/release.yml:217:            gh release create "$TAG" --repo "$GITHUB_REPOSITORY" --verify-tag "${RELEASE_FLAGS[@]}" \
.github/workflows/release.yml:219:              --notes "Binaries built by this workflow. Verify the SHA256 before running anything." \
.github/workflows/release.yml:222:          gh release upload "$TAG" dist/* --clobber --repo "$GITHUB_REPOSITORY"
docs/AUDIT-2026-09-08.md:7:The Rust baseline is release v0.9.5, commit
docs/AUDIT-2026-09-08.md:9:112 Rust source and crate Cargo.toml files matched the local release mirror.
docs/AUDIT-2026-09-08.md:17:Website-only changes described below are not in the release tag.
docs/AUDIT-2026-09-08.md:49:Tests cover a second holder, release/reacquire and separate directories.
docs/AUDIT-2026-09-08.md:97:or establish present hashrate ownership.

```

## NF-REL-010 - release_security_terms

Status: `PASS`

Class: `security_boundary`

Command:

```bash
grep -RniE 'signed|signature|notar|reproducible|binary|artifact|supply chain' .github docs SECURITY.md 2>/dev/null | head -120
```

Stdout:

```text
09-08.md:147:## Reproducible sources
docs/SWAP-ATTACKS.md:30:| Signed lying payload | `hostile_payload_tests` | `BadPayload`; still spendable from `t` |
docs/SWAP-ATTACKS.md:50:- Fee-ladder pre-signed rungs (handshake still signs one fee).
docs/SWAP-VAULT-PROGRESS-2026-09-13.md:51:wallets. Mainnet stays closed. Dedicated backup recovery, signed fee variants
docs/SWAP-VAULT-PROGRESS-2026-09-13.md:69:  **single-fee protocol**, not to a signed ladder. Selecting a helper rung
docs/SWAP-VAULT-PROGRESS-2026-09-13.md:95:signed fee ladder. No gate was opened. The `/private/tmp` logs from that run
docs/SWAP-VAULT-PROGRESS-2026-09-13.md:120:3. **Versioned signed-fee protocol.** Negotiate and authenticate all variants;
docs/SWAP-VAULT-PROGRESS-2026-09-13.md:124:   fee and one signature per leg; incompatible variants must not masquerade as
docs/SWAP-VAULT-PROGRESS-2026-09-13.md:138:   fresh artifacts, verify version/network isolation and downloads, then use
docs/DECISIONS.md:12:| 2 | Value soundness | **Schnorr excess signature over generator `H`** proving the excess has no `G` component, plus **Bulletproof range proofs** on every output. Replaces the v4 "balance proof", which proved nothing at all. |
docs/DECISIONS.md:25:| 15 | Block structure | **Aggregated.** A block holds one flat, canonically sorted set of inputs, outputs and kernels; transactions do not survive into it. Kernels therefore sign only their own fields, and output integrity moved to a per-output sender signature. |
docs/DECISIONS.md:26:| 16 | Cut-through | **Not applied.** It would delete the per-input signature that makes one-sided payments safe. Choosing non-interactive payments (row 4) rules it out. Documented rather than hidden. |
docs/DECISIONS.md:32:- **Cut-through**, or a spend-authorisation scheme that does not require a per-input signature. Until then the transaction graph is obscured, not erased.
docs/whitepaper-en.json:23:          "text": "The central design choice is to combine private payment amounts with an explicit supply invariant. Nodes check a relationship between unspent commitments, accumulated kernel excesses, issuance and burned fees. That relationship is useful only together with valid range proofs, signatures, authorization and correct state transitions. An equation by itself is not a security proof."
docs/whitepaper-en.json:107:              "Queries and signed transactions",
docs/whitepaper-en.json:129:          "text": "Consensus rules do not remove implementation or distribution trust. A user still chooses a client binary, its checkpoint policy, an operating system and a way to obtain peers. These dependencies are made explicit throughout this paper."
docs/whitepaper-en.json:159:          "text": "The output carries a commitment, range proof, ephemeral key, one-time public key, view tag, encrypted payload and sender signature. The receiver scans for matching outputs, decrypts the value and memo, and checks that the recovered opening recreates the published commitment. A successfully decrypted payload alone is not enough."
docs/whitepaper-en.json:210:              "Signatures",
docs/whitepaper-en.json:233:          "text": "Commitments and range proofs use the same generator pair from PedersenGens. Binding relies on the assumed hardness of finding the discrete-log relation between G and H. Proof and signature checks must reject invalid encodings and bind the intended context. Bulletproofs require no trusted setup, but that property does not certify Nightfall's application of them."
docs/whitepaper-en.json:268:          "text": "For an ordinary transfer, output value plus the public fee equals input value. Its remaining commitment difference is a blinding excess. Kernels carry Schnorr signatures relative to H. The verifier requires both the expected excess and valid signatures; merely publishing the publicly computable difference would prove nothing."
docs/whitepaper-en.json:280:          "text": "Starting from the defined genesis state, accepted transitions preserve this invariant. Range proofs exclude invalid value encodings; input signatures establish spending authority; UTXO checks prevent double spending; emission rules bound coinbase issuance. Removing any of these checks changes the security argument."
docs/whitepaper-en.json:532:              "An opening and signature for one output. A narrower statement than sharing a view key."
docs/whitepaper-en.json:542:          "text": "A receipt discloses an individual commitment opening and a signature by the address's spend key. Verification checks the opening and signature. A verifier still needs appropriate chain evidence to establish inclusion and confirmation; the receipt alone does not establish that the output remains unspent."
docs/whitepaper-en.json:553:              "Opening and signature"
docs/whitepaper-en.json:667:          "text": "These mechanisms are inspired by Dandelion research; the paper's formal guarantees cannot simply be assigned to this implementation.
```
