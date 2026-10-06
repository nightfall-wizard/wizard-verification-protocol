# WVP Release-Reality Threat Model

## Assets protected

- claim boundary integrity
- user interpretation of release evidence
- repository safety expectations
- release artifact verification semantics

## Threats

| Threat | Mitigation |
|---|---|
| Metadata mistaken for security proof | Hard non-claim list remains in output |
| Missing signatures treated as success | Classifier returns WARN |
| Failed checksum treated as warning | Classifier returns FAIL |
| Failed signature treated as warning | Classifier returns FAIL |
| CLI input used as shell command text | Target parser restricts owner/repo shape |
| Release binaries executed during verification | Verification code only hashes/verifies artifacts |
| JSON output injection through errors | Report uses serde_json escaping |

## Non-goals

This is not a cryptographic audit, consensus audit, wallet audit, legal assessment, or investment assessment.
