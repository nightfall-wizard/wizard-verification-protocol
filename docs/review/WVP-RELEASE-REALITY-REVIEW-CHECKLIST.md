# WVP Release-Reality Review Checklist

Reviewers should check:

- [ ] `main.rs` is only CLI glue.
- [ ] Live GitHub access is isolated from classification.
- [ ] INFO cannot occur without checksum and signature verification passing.
- [ ] Checksum failure produces FAIL.
- [ ] Signature failure produces FAIL.
- [ ] Missing evidence stays WARN, not INFO.
- [ ] JSON output remains parseable with escaped error strings.
- [ ] No release binary is executed.
- [ ] No seed, private key, token, wallet, custody, or user-funds data is read.
- [ ] No audit, legal, investment, custody, binary-safety, source-to-binary, or reproducible-build claim is added.
- [ ] Existing conformance output remains compatible.
