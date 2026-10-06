# AUNEYA Local Claim Selection v0.1

Status: protocol research
Scope: local Termux simulation
Value status: non-value simulation only

## Purpose

This document defines the first local AUNEYA claim selection tool.

The selector allows a Termux user to choose between supported lawful public claim fixtures before running the local demo.

## Supported local claim keys

- release-reality
- download-integrity
- website-claim-reality

## List supported claims

python3 tools/auneya/auneya_local_claim_select.py --list

## Select one claim

python3 tools/auneya/auneya_local_claim_select.py --claim-key release-reality

## Print selected claim path

python3 tools/auneya/auneya_local_claim_select.py --claim-key release-reality --print-path

## Run local demo with selected claim

python3 tools/auneya/auneya_local_claim_select.py --claim-key release-reality --run-demo

Other supported examples:

python3 tools/auneya/auneya_local_claim_select.py --claim-key download-integrity --run-demo

python3 tools/auneya/auneya_local_claim_select.py --claim-key website-claim-reality --run-demo

## Legal boundary

Only supported lawful public or owner-authorized fixtures are accepted.

Private-data claims are not accepted.

Claims requiring authentication are not accepted.

Claims requiring payment are not accepted.

Claims containing personal data are not accepted.

Claims requiring credential use, paywall bypass, hacked data or surveillance are not accepted.

## Non-Value Boundary

The selector does not create a token.

The selector does not create AUNEYA.

The selector does not create neya.

The selector does not create a real reward.

The selector does not create market value.

The selector does not activate a mainnet.

The selector does not perform mining.

Selected claims only feed the local non-value demo.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `tools/auneya/auneya_local_claim_select.py`
- `conformance/auneya-local-claim-selection-v0.1.sh`
