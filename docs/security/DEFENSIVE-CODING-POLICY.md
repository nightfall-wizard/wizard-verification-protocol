# WVP Defensive Coding Policy

## Purpose

This policy defines defensive coding rules for WVP production Rust code.

WVP is security-sensitive release verification software. Production code must avoid avoidable crash paths, ambiguous failures, debugging leftovers, and silent trust upgrades.

The goal is not cosmetic style enforcement. The goal is measurable risk reduction.

---

## Scope

This policy applies to production Rust code under:

- `reference/rust/wvp-release-check/src`

It does not apply to test code, fixtures, generated baselines, or documentation.

---

## Risk Patterns

The following patterns are treated as security-relevant risk indicators in production code:

| Pattern | Risk |
|---|---|
| `unwrap(` | uncontrolled panic path |
| `.unwrap()` | uncontrolled panic path |
| `expect(` | uncontrolled panic path with message |
| `.expect()` | uncontrolled panic path with message |
| `panic!` | explicit crash path |
| `todo!` | incomplete production behavior |
| `unimplemented!` | incomplete production behavior |
| `dbg!` | debug leakage / accidental output |
| `unsafe` | memory-safety or FFI risk |
| `allow(unused` | potential dead-path hiding |
| `allow(dead_code` | potential dead-path hiding |

---

## Baseline Rule

Existing findings are recorded in:

- `security-baselines/rust-risk-patterns.baseline`

The CI gate fails if the count for any tracked risk pattern increases.

This means:

1. existing risk is visible,
2. new risk cannot silently enter,
3. reductions are measurable,
4. future cleanup can ratchet the baseline downward.

---

## Review Rule

Any pull request that increases a defensive-code risk pattern must either:

1. remove the new pattern,
2. replace it with explicit error handling,
3. justify it in documentation,
4. update the baseline only after deliberate review.

---

## Preferred Alternatives

Instead of `unwrap` or `expect`, production code should prefer:

- explicit `Result`
- typed errors
- graceful failure
- fail-closed classification
- deterministic error reporting

Instead of `panic!`, production code should prefer:

- returning an error,
- rejecting invalid input,
- classifying the state as failed,
- preserving enough context for review.

---

## Security Principle

Production verification code must not convert malformed, missing, ambiguous, or adversarial input into uncontrolled process failure unless that behavior is explicitly documented and intentionally accepted.

