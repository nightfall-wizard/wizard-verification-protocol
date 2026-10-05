# WVP Limitations

WVP does not prove that a cryptocurrency protocol is secure.

Current bootstrap limitations:

- no full GitHub release API verification yet
- no signature validation yet
- no checksum validation yet
- no reproducible build verification yet
- no Nightfall report yet
- no scorecard module yet
- no node diagnostic module yet
- no light verification module yet

<!-- WVP:ANDROID-VS-CI-CONFORMANCE-LIMITATIONS:START -->
## Android vs CI Build Provenance Limitations

Android-vs-CI build-provenance comparison is useful evidence, but it is deliberately limited.

It does not prove:

- that the binary is safe;
- that the published release asset was built from the source tree;
- that the build is reproducible;
- that cross-architecture binaries should be byte-identical;
- that the project has been audited.

It only proves that, for the checked-out commit and selected GitHub Actions artifact, WVP can compare Android-Termux and GitHub Actions build-provenance artifacts while keeping the claim boundary explicit.
<!-- WVP:ANDROID-VS-CI-CONFORMANCE-LIMITATIONS:END -->

