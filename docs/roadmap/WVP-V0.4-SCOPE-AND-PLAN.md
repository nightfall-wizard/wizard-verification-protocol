# WVP v0.4 Scope and Execution Plan

Status: planned.

## Purpose

WVP v0.4 starts after the successful v0.3 publication and post-release verification.

v0.3 proved the release-check publication path:

- release asset staging;
- detached signature creation;
- public verification key publication;
- GitHub release publication;
- post-release download verification;
- CI-backed release-state conformance.

v0.4 moves from release publication integrity toward broader WVP capability expansion.

## Legal and safety priority

Legal compliance and safety are the first constraint.

WVP v0.4 must not introduce:

- custody functionality;
- exchange, broker, or trading functionality;
- investment advice automation;
- private-key collection;
- seed phrase collection;
- wallet-spending automation;
- admin-mint or privileged monetary controls;
- claims of audit, certification, legal compliance, or binary safety without independent evidence.

WVP remains a verification and diagnostics project, not a financial service.

## v0.4 module tracks

### Track 1 — release-check hardening

Goal:

- make `wvp-release-check` more robust against malformed GitHub release states.

Planned work:

- stricter asset classification;
- clearer status categories;
- deterministic JSON output;
- explicit negative tests for duplicated assets;
- explicit negative tests for missing public verification key;
- clearer distinction between metadata discovery, checksum verification, and signature verification.

Exit evidence:

- unit tests;
- conformance scripts;
- documented limitations.

### Track 2 — scorecard security baseline

Goal:

- add a lightweight repository security scorecard.

Initial scope:

- repository metadata checks;
- release asset checks;
- branch/protection visibility where available;
- dependency-lockfile presence;
- CI presence;
- signing-material hygiene;
- no-secret policy.

Non-goals:

- no audit;
- no vulnerability certification;
- no exploit guarantee;
- no legal compliance guarantee.

Exit evidence:

- JSON scorecard output;
- conformance checks;
- clear limitation text.

### Track 3 — node-diagnose read-only diagnostics

Goal:

- design a read-only node diagnostic module.

Allowed scope:

- local node status;
- peer count;
- sync height;
- RPC availability;
- version visibility;
- non-mutating diagnostics only.

Forbidden scope:

- no wallet spending;
- no seed handling;
- no private-key handling;
- no chain mutation;
- no automated legal or investment claims.

Exit evidence:

- read-only command design;
- safety boundary tests;
- documentation.

### Track 4 — conformance and test vectors

Goal:

- make WVP behavior easier to reproduce and verify.

Planned work:

- stable example JSON fixtures;
- positive and negative fixtures;
- regression tests for release states;
- conformance runner documentation.

Exit evidence:

- fixture directory;
- conformance script;
- CI coverage.

### Track 5 — light-verify design phase

Goal:

- plan a future light verification module without overclaiming.

Potential future checks:

- header linkage;
- height monotonicity;
- network id;
- checkpoint matching;
- proof-of-work field sanity;
- cumulative-work representation;
- overflow guards.

v0.4 scope is planning and safe scaffolding only unless explicitly implemented later.

Non-goals:

- no full-node security equivalence claim;
- no consensus audit;
- no finality guarantee;
- no wallet custody.

## v0.4 execution order

Recommended order:

1. harden `wvp-release-check`;
2. create scorecard skeleton;
3. create node-diagnose design document;
4. add conformance fixture strategy;
5. prepare light-verify threat model;
6. run CI after every small commit.

## Evidence boundary

v0.4 planning does not prove:

- audit result;
- legal compliance;
- binary safety;
- source-to-release correspondence;
- reproducible build;
- consensus correctness;
- wallet safety;
- investment suitability.

## Progress interpretation

After this plan is merged:

- WVP v0.3 publication/post-release remains complete for publication only;
- WVP v0.4 is planned but not implemented;
- overall WVP system is not complete.
