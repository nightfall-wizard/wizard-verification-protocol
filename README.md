# Wizard Verification Protocol (WVP) & AUNEYA

**Built and maintained by [nightfall-wizard](https://github.com/nightfall-wizard).**

> No claim without proof. No proof without reproduction. No verification without adversarial testing.

[![Published WVP](https://img.shields.io/github/v/release/nightfall-wizard/wizard-verification-protocol?include_prereleases=false&label=WVP%20published)](https://github.com/nightfall-wizard/wizard-verification-protocol/releases/latest)
[![README truth](https://github.com/nightfall-wizard/wizard-verification-protocol/actions/workflows/readme-truth.yml/badge.svg)](https://github.com/nightfall-wizard/wizard-verification-protocol/actions/workflows/readme-truth.yml)

## The two-layer vision

**WVP** is an evidence-first, adversarial verification framework for reproducible checks of public software and project claims.
**AUNEYA** researches a phone-first witness protocol for lawful public digital evidence.
WVP is its verification core; AUNEYA is the proposed network layer, not an already operating public network.

<!-- WVP-RELEASE-TRUTH:START -->
## Release truth — independent identities

| Track | Verified status |
| --- | --- |
| WVP published stable | **[v0.5.1](https://github.com/nightfall-wizard/wizard-verification-protocol/releases/tag/v0.5.1)** · [always-current release](https://github.com/nightfall-wizard/wizard-verification-protocol/releases/latest) |
| WVP source package | **`0.5.1`** · [`Cargo.toml`](reference/rust/wvp-release-check/Cargo.toml); source is not a release |
| AUNEYA published research preview | **[auneya-v1.5.0](https://github.com/nightfall-wizard/wizard-verification-protocol/releases/tag/auneya-v1.5.0)** · distinct from WVP |
| AUNEYA research implementation | **v1.9** · [signed replay checkpoints](docs/auneya/AUNEYA-EXTERNAL-REPLAY-ANCHORS-V1.9.md); not a published v1.9 release |

*Release API snapshot checked on 2026-10-30T21:34:53Z UTC; this snapshot is not real-time.
The WVP `releases/latest` link is live. Source: [`published release evidence`](docs/status/WVP-AUNEYA-PUBLISHED-RELEASES.json).*
<!-- WVP-RELEASE-TRUTH:END -->

## WVP verification surface

- [Rust release checker](reference/rust/wvp-release-check/src/lib.rs) and [adversarial classification tests](reference/rust/wvp-release-check/tests/adversarial_classification.rs) separate recorded evidence from unsupported release claims.
- [Release-truth guard](tools/wvp_release_truth.py) distinguishes published WVP, source packages and AUNEYA research versions.
- [Evidence-first release policy](docs/release/WVP-RELEASE-TRUTH-AND-AUNEYA-GATES.md) documents strict claim boundaries.

## AUNEYA implemented research milestones

Each row links to committed source, an engineering document and an adversarial test file.
**File existence is evidence of implementation, not proof that an independent audit passed.**

| Version | Capability | Source / specification / tests |
| --- | --- | --- |
| v0.5 | Signed challenges | [code](tools/auneya/auneya_nightfall_challenge_v05.py) · [spec](docs/auneya/AUNEYA-NIGHTFALL-CHALLENGE-V0.5.md) · [tests](tests/test_auneya_nightfall_challenge_v05.py) |
| v0.6 | Registry checkpoint binding | [code](tools/auneya/auneya_registry_checkpoint_v06.py) · [spec](docs/auneya/AUNEYA-REGISTRY-CHECKPOINT-V0.6.md) · [tests](tests/test_auneya_registry_checkpoint_v06.py) |
| v0.7 | Pinned observations | [code](tools/auneya/auneya_pinned_observation_v07.py) · [spec](docs/auneya/AUNEYA-PINNED-OBSERVATION-V0.7.md) · [tests](tests/test_auneya_pinned_observation_v07.py) |
| v0.8 | Multi-witness evidence | [code](tools/auneya/auneya_wvp_evidence_batch_v08.py) · [spec](docs/auneya/AUNEYA-WVP-EVIDENCE-BATCH-V0.8.md) · [tests](tests/test_auneya_wvp_evidence_batch_v08.py) |
| v0.9 | Canonical evidence archives | [code](tools/auneya/auneya_archive_v09.py) · [spec](docs/auneya/AUNEYA-ARCHIVAL-EVIDENCE-V0.9.md) · [tests](tests/test_auneya_archive_v09.py) |
| v1.0 | Transactional archives | [code](tools/auneya/auneya_archive_v10.py) · [spec](docs/auneya/AUNEYA-TRANSACTIONAL-ARCHIVE-V1.0.md) · [tests](tests/test_auneya_archive_v10.py) |
| v1.1 | Federated evidence research | [code](tools/auneya/auneya_federation_v11.py) · [spec](docs/auneya/AUNEYA-FEDERATED-WITNESS-EVIDENCE-V1.1.md) · [tests](tests/test_auneya_federation_v11.py) |
| v1.2 | Portable offline verification | [code](tools/auneya/auneya_portable_v12.py) · [spec](docs/auneya/AUNEYA-PORTABLE-FEDERATION-V1.2.md) · [tests](tests/test_auneya_portable_v12.py) |
| v1.3 | Independent Ed25519 verification | [code](tools/auneya/auneya_independent_v13.js) · [spec](docs/auneya/AUNEYA-INDEPENDENT-VERIFICATION-V1.3.md) · [tests](tests/test_auneya_independent_v13.py) |
| v1.4 | Lossless cross-language interop | [code](tools/auneya/auneya_independent_v14.js) · [spec](docs/auneya/AUNEYA-LOSSLESS-INTEROPERABILITY-V1.4.md) · [tests](tests/test_auneya_independent_v14.py) |
| v1.5 | Temporal evidence admission | [code](tools/auneya/auneya_admission_v15.py) · [spec](docs/auneya/AUNEYA-TEMPORAL-ADMISSION-V1.5.md) · [tests](tests/test_auneya_admission_v15.py) |
| v1.6 | Signed peer-envelope admission | [code](tools/auneya/auneya_peer_gate_v16.py) · [spec](docs/auneya/AUNEYA-PEER-EVIDENCE-GATE-V1.6.md) · [tests](tests/test_auneya_peer_gate_v16.py) |
| v1.7 | Bounded local TCP transport | [code](tools/auneya/auneya_transport_v17.py) · [spec](docs/auneya/AUNEYA-TRANSPORT-V1.7.md) · [tests](tests/test_auneya_transport_v17.py) |
| v1.8 | Authenticated local receipts | [code](tools/auneya/auneya_receipt_v18.py) · [spec](docs/auneya/AUNEYA-AUTHENTICATED-RECEIPTS-V1.8.md) · [tests](tests/test_auneya_receipt_v18.py) |
| v1.9 | Signed offline replay checkpoints | [code](tools/auneya/auneya_anchor_v19.py) · [spec](docs/auneya/AUNEYA-EXTERNAL-REPLAY-ANCHORS-V1.9.md) · [tests](tests/test_auneya_anchor_v19.py) |

## Roadmap and research gates

Based on the [v1.9 engineering roadmap](docs/auneya/AUNEYA-ROADMAP-V1.9.md):

| Gate | Current evidence boundary |
| --- | --- |
| 1 · Authenticated peer evidence | Implemented as local research capability (v1.6) |
| 2 · Peer transport | Partially implemented: bounded localhost TCP + signed responder receipts (v1.7/v1.8) |
| 3 · External replay anchors | Partially implemented: offline operator-signed chained checkpoints (v1.9); no independently proven remote retention |
| 4 · Public reproducibility | Incomplete: normative schemas, interoperability and independent replication remain |
| 5 · External validation | Not completed: real second-device trials, independent cryptographic/privacy/security/legal reviews |
| 6 · Production decision | **BLOCKED** · no automatic network or economic activation |

**Next engineering priority (Gate 3):** independently retained high-water replay checkpoints,
rollback/recovery attack tests across distinct devices, and reproducible signed acceptance vectors.
The existing v1.9 checkpoint file stored beside its database is **not** an independent anchor.

## Start and reproduce locally (Termux)

```sh
./tools/auneya/auneya_one_command_local_demo.sh
python3 -m unittest discover -s tests -p "test_auneya_anchor_v19.py" -v
python3 -m unittest discover -s tests -p "test_wvp_release_truth.py" -v
python3 tools/readme_truth.py --check
```

The demo is **local non-value simulation**, not real token collection.
Cryptographic tests may require `openssl` and `node` on the device.
The README checker validates traceability and freshness against the checked-in release snapshot.

## Canonical project documents

- [Protocol Charter](docs/auneya/AUNEYA-PROTOCOL-CHARTER.md) — purpose, legal and economic boundaries.
- [AUNEYA technical whitepaper v0.1 DRAFT](docs/auneya/AUNEYA-WHITEPAPER-V0.1-DRAFT.md) — research, **not** final protocol approval.
- [AUNEYA engineering roadmap v1.9](docs/auneya/AUNEYA-ROADMAP-V1.9.md) — six gates and remaining work.
- [WVP release identity policy](docs/release/WVP-RELEASE-TRUTH-AND-AUNEYA-GATES.md) — release/source distinction.
- [Security disclosures](SECURITY.md) · [MIT license](LICENSE).

## Security and honest claim boundaries

WVP/AUNEYA currently **do not claim**: an independent security audit;
independent witness/device identity; public P2P networking; global consensus;
Sybil resistance; trusted time; distributed rollback immunity; reproducible binary builds;
mainnet readiness; economic activation; transferable units; or legal clearance.
An Ed25519 signature proves possession of a signing key, not observer independence or factual truth.

<!-- WVP-V050-PUBLISHED:START -->
## Historical release notes

WVP [v0.5.0](https://github.com/nightfall-wizard/wizard-verification-protocol/releases/tag/v0.5.0) is an already published historical release,
not an unreleased source candidate.
<!-- WVP-V050-PUBLISHED:END -->
<!-- WVP:V040-PUBLIC-STATUS:START -->

**HISTORICAL SNAPSHOT ONLY:** WVP
[v0.4.0](https://github.com/nightfall-wizard/wizard-verification-protocol/releases/tag/v0.4.0) was published;
older prepared-not-released records describe a past pre-publication stage, not current status.
Earlier README text is preserved in Git history.
<!-- WVP:V040-PUBLIC-STATUS:END -->

## Maintainer workflow

The README is generated by [`tools/readme_truth.py`](tools/readme_truth.py) and checked by
[CI](.github/workflows/readme-truth.yml). To refresh against public GitHub release facts,
run `python3 tools/readme_truth.py --refresh` in an authenticated Termux environment.
A scheduled CI check detects release changes; it does **not** silently modify releases or the protocol.
