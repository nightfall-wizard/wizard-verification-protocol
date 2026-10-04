# WVP Release Integrity Spec

## Purpose

wvp-release-check evaluates release integrity signals for Rust cryptocurrency projects.

It does not prove that a release is secure.

## Evidence classes

- verified
- observed
- not found
- not verified
- out of scope
- limitation

## Target checks

A complete implementation should inspect:

1. GitHub releases
2. Git tags
3. release assets
4. checksums
5. signatures
6. build instructions
7. reproducible build notes
8. source archive availability
9. CI status around release
10. explicit limitations

## Required output

- target repository
- inspected tag or release
- timestamp
- tool version
- checks performed
- PASS/WARN/FAIL/INFO classifications
- limitations
- reproducible command

## Safety rule

The tool must not read wallet files, seeds, private keys or local node datadirs.
