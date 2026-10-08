# AUNEYA Adversarial Invariant Matrix v0.1

AUNEYA is documented as a permissionless Layer One research implementation and phone-first witness network.

This document defines adversarial protocol invariants for future AUNEYA Layer One research work.

It is compatible with AUNEYA L1 Legal Boundary v0.1.

## Status

- Research-mode invariant set
- Implementation-agnostic
- Non-value protocol safety document
- No token sale
- No market-value claim
- No custody design
- No exchange, broker, advice or transfer-service framing

## Purpose

The purpose of this matrix is to define what must remain true even when the network is exposed to hostile peers, malformed data, replay attempts, spam, censorship pressure, fork pressure, timing manipulation or witness abuse.

These invariants are not a mainnet launch plan. They are a safety baseline for future test vectors, reference implementations and conformance checks.

## Terms

- Invariant: a property that must remain true under adversarial pressure.
- Adversary: any peer, client, witness, miner, validator, relay, wallet, script or operator that behaves unexpectedly or maliciously.
- Witness: a protocol participant that may observe, attest or verify protocol-relevant data.
- Payload hash: a cryptographic commitment to the data being attested or verified.
- Fail closed: reject, stop or quarantine unsafe state instead of accepting ambiguous state.

## Invariant matrix

| ID | Invariant | Adversarial pressure | Required property | Failure condition | Test hook |
|---|---|---|---|---|---|
| AUNEYA-INV-001 | Chain identity is immutable | Wrong chain identifier | A node rejects data for a different chain id | Cross-chain data is accepted | Chain-id mismatch fixture |
| AUNEYA-INV-002 | Block validation is deterministic | Different devices validate the same block | Validity result must not depend on device, locale or wall-clock formatting | Two honest implementations disagree | Deterministic validation fixture |
| AUNEYA-INV-003 | Unsigned state transitions are rejected | Malformed or unsigned transaction | No unsigned state transition may alter state | Unsigned data changes state | Signature-required fixture |
| AUNEYA-INV-004 | Replay attempts are rejected | Old transaction is resent | Nonce, sequence or equivalent replay control must prevent duplicate execution | Same transition executes twice | Replay fixture |
| AUNEYA-INV-005 | Time assumptions are bounded | Hostile timestamp or clock skew | Timestamp logic must have explicit bounds | Far-future or far-past data is accepted without rule | Timestamp-bound fixture |
| AUNEYA-INV-006 | Witness attestation binds to payload hash and chain id | Attestation is reused for another payload or chain | An attestation must be invalid outside its exact payload and chain context | Valid attestation is replayed elsewhere | Attestation-binding fixture |
| AUNEYA-INV-007 | Witness cannot custody assets or authorize user state alone | Witness overreach | Witness role must not become custody, broker, exchange, advice or unilateral transfer authority | Witness can move third-party state alone | Witness-authority fixture |
| AUNEYA-INV-008 | Equivocation evidence is representable | Same actor signs conflicting claims | Conflicting claims must be expressible as evidence | Conflicting claims cannot be recorded or tested | Equivocation fixture |
| AUNEYA-INV-009 | Peer input is untrusted by default | Malicious peer messages | Peer data must be validated before use | Raw peer input is trusted as canonical | Peer-input fixture |
| AUNEYA-INV-010 | Genesis configuration is immutable for a chain id | Genesis mutation | A chain id must bind to exactly one genesis configuration | Same chain id accepts different genesis config | Genesis-lock fixture |
| AUNEYA-INV-011 | State transition errors fail closed | Parser, storage or validation error | Error paths must not commit partial unsafe state | Partial invalid state is committed | Fail-closed fixture |
| AUNEYA-INV-012 | Protocol logs must not contain secrets | Debug or crash logs | Logs must not expose private keys, seeds, signing material or secret recovery material | Secret material appears in logs | Secret-log fixture |
| AUNEYA-INV-013 | Economic features are disabled in research mode | Premature value framing | Research mode must not activate public sale, presale, allocation sale, market-value claim or transferable economic launch | Research mode enables economic launch framing | Research-boundary fixture |
| AUNEYA-INV-014 | Legal boundary compatibility is mandatory | Conflicting document or implementation | The stricter non-value interpretation controls until separate legal review approves a change | A technical step conflicts with the legal boundary | Legal-boundary fixture |
| AUNEYA-INV-015 | Spam resistance must be explicit | Message flooding | Any future networking or mempool design must define resource limits | Unbounded peer spam is accepted | Spam-limit fixture |
| AUNEYA-INV-016 | Censorship assumptions must be documented | Selective relay or block omission | Censorship resistance assumptions must be explicit and testable | Censorship risk is hidden or undocumented | Censorship fixture |

## Hard stops

A future AUNEYA implementation must stop before release promotion if any of the following is true:

1. AUNEYA-INV-001 through AUNEYA-INV-016 are not documented.
2. A conformance suite cannot represent the invariant.
3. A test vector contradicts the invariant.
4. A witness can custody third-party assets.
5. A witness can authorize third-party state movement alone.
6. Research mode enables sale, presale, allocation sale, market-value claim or transferable economic launch framing.
7. Any implementation conflicts with AUNEYA L1 Legal Boundary v0.1.

## Non-goals

This document does not define a public mainnet launch, token sale, presale, allocation sale, exchange listing, custody service, broker service, advisory service, transfer service or market-value communication.

## Implementation rule

Future AUNEYA technical steps must reference this matrix when introducing networking, witness logic, transaction validation, replay protection, attestation logic, state transition logic or research-mode controls.
