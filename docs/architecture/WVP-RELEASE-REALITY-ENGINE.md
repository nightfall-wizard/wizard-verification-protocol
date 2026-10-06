# WVP Release-Reality Engine Architecture

## Purpose

The release-reality engine separates verification policy from live GitHub access and CLI rendering.

The goal is not to make stronger claims. The goal is to make the existing claim boundary easier to review, test, and maintain.

## Boundaries

| Layer | Responsibility | Must not do |
|---|---|---|
| CLI | Parse command-line flags and call the library | Decide trust status |
| Model | Define typed observations and targets | Perform I/O |
| Provider | Collect evidence from GitHub or fixtures | Interpret security meaning |
| Verify | Check checksum and detached signature artifacts | Execute release binaries |
| Classify | Convert observations into INFO/WARN/FAIL | Read network or filesystem |
| Report | Render stable human/JSON output | Change verification meaning |

## Security posture

The engine treats missing evidence as a warning, failed verified evidence as failure, and offline metadata-only output as non-success.

INFO requires both checksum and signature verification to pass.

## Explicit non-claims

This engine does not prove:

- binary safety
- source-to-binary correspondence
- reproducible builds
- external audit status
- legal clearance
- investment quality
- custody safety
