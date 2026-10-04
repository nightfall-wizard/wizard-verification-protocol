# WVP Signature Tamper-Negative Testing

WVP v0.2 verifies that detached signature verification fails when release inputs are modified.

## Covered cases

The Rust reference implementation tests:

- valid detached signature passes
- modified signed asset fails
- modified detached signature fails
- wrong public verification key fails

## Method

The tests create temporary signing material in a test-only temporary directory.

The generated signing material is not committed.

The generated signing material is not printed.

The generated signing material is removed after the test.

## Expected policy

A release verifier must not treat signature asset discovery as signature verification.

A release verifier must fail closed when signature verification is attempted and fails.

## Scope

This is not an audit.

This does not prove reproducible builds.

This proves the local detached signature verification primitive rejects common tampering cases.
