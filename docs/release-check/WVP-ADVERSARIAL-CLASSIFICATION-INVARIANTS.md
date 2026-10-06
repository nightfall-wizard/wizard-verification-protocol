# WVP adversarial classification invariants

## Purpose

This document defines the trust boundary for WVP release-check classification.

The classifier must fail closed. It must not upgrade incomplete, ambiguous or adversarial release evidence to `INFO`.

## Hard invariants

`INFO` is reachable only when all of the following are true:

- execution is live;
- repository existence is positively confirmed;
- at least one release is observed;
- the latest release is positively found;
- the latest release tag is non-empty;
- exactly one checksum asset is observed;
- exactly one detached signature asset is observed;
- checksum verification is attempted and passes;
- detached signature verification is attempted and passes;
- no provider errors are present.

## Negative evidence

The classifier must not return `INFO` for:

- offline mode;
- missing metadata;
- duplicate checksum assets;
- duplicate signature assets;
- missing release tag;
- failed checksum verification;
- failed signature verification;
- provider errors.

## Non-claims

This invariant gate does not claim:

- external audit status;
- binary safety;
- source-to-release proof;
- reproducible builds;
- legal compliance;
- wallet safety;
- investment suitability.

## Review focus

Review should focus on whether the classifier reduces long-term release-integrity risk by making false-positive `INFO` states harder to create.
