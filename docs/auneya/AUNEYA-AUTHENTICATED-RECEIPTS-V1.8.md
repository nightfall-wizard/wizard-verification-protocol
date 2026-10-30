# AUNEYA/WVP v1.8

## Authenticated Local Receipt Protocol

Status: Non-value research implementation.

No public network or economic activation.

## 1. Problem

AUNEYA v1.7 authenticates inbound Ed25519
peer messages.

However, v1.7 returns an unauthenticated
JSON acknowledgment.

Consequently, the sender cannot independently
authenticate an ACCEPTED response.

## 2. v1.8 Solution

Introduce a domain-separated signed receipt
authenticated by an independently pinned
responder public key.

The sender supplies a fresh random 32-byte
nonce for each individual request.

The server binds the resulting receipt to:

- AUNEYA research chain identity
- Signed message sender
- Complete request-frame SHA-256
- Client-generated nonce
- Responder public-key SHA-256
- Admission status
- Local replay persistence status
- Non-value research boundary

The signed payload is canonical ASCII JSON.

Signature algorithm:

Ed25519.

Domain:

AUNEYA/WVP:RECEIPT:V1.8 followed by NUL.

## 3. Transport

The implementation accepts connections
only on 127.0.0.1.

Wire request:

32-byte random nonce

followed by

4-byte big-endian signed-envelope length

followed by

unchanged canonical v1.6 peer envelope.

The client then performs TCP write half-close.

The server requires EOF after the request.

The server verifies the incoming message using
the existing v1.6/v1.7 security mechanisms.

A valid response contains a signed receipt.

## 4. Cryptographic Verification

The client verifies:

- Exact response structure
- Canonical JSON
- Bounded response length
- Expected research chain
- Expected original sender
- Matching request SHA-256
- Matching fresh nonce
- Independently pinned responder key
- Valid Ed25519 signature
- Internally consistent admission status

Invalid responses fail closed.

A response without a valid signature is not
considered an authenticated acknowledgment.

## 5. Replay and Persistence

The existing v1.6 persistent SQLite replay
mechanism remains authoritative.

AUNEYA v1.8 does not reset or bypass
the existing replay ledger.

Important limitation:

A message can be committed to the local
replay database before the server sends
its signed response.

If the signing process or connection fails,
the sender does not know whether admission
was committed.

A lost acknowledgment must therefore be
treated as an unknown outcome.

It is not evidence that admission failed.

The client must not automatically reuse
the same signed counter assuming rollback.

## 6. Resource Limits

Maximum incoming signed frame:

65,536 bytes.

Client nonce:

32 bytes.

Maximum response:

2,048 bytes.

Complete request deadline:

2 seconds.

Maximum connections per server invocation:

64.

TCP binding:

127.0.0.1 only.

Processing:

Bounded and serial.

Cryptographic subprocess deadline:

4 seconds.

## 7. Security Boundaries

This implementation does not establish:

- Public peer-to-peer networking
- Independent physical-device identity
- Network-wide replay protection
- Trusted global time
- External rollback protection
- Sybil resistance
- Distributed consensus
- Formal finality
- Independent cryptographic audit
- Production readiness
- Token issuance
- Economic activation

A signed acknowledgment proves that the
configured responder signing key authenticated
the response.

It does not prove a globally agreed state.

## 8. Key Management

The responder uses a separate Ed25519
key pair.

Private keys must remain outside Git.

Private PEM files require permissions 0600.

The public responder key must be verified
against an independently trusted SHA-256 pin.

The same potentially compromised source must
not be treated as independent confirmation
of its own key identity.

The server verifies that its configured
private key matches the pinned public key
before accepting network requests.

## 9. Verification

Run:

    python3 -m unittest discover \
      -s tests \
      -p 'test_auneya_receipt_v18.py' \
      -v

GitHub Actions:

    .github/workflows/auneya-receipt-v18.yml

The tests use real cryptographic keys and
actual TCP loopback sockets.

Covered failure classes include:

- Forged peer signatures
- Forged responder signatures
- Wrong responder fingerprints
- Modified signed receipts
- Replayed acknowledgment nonces
- Persistent message replay
- Revoked peer identities
- Invalid message framing

## 10. Next Development Gates

Gate 3:

Externally anchored monotonic replay state.

Gate 4:

Cross-implementation reproducibility.

Gate 5:

Independent physical-device experiments,
cryptographic review, privacy review and
adversarial network testing.

Gate 6:

Separate production authorization.

No source-code merge automatically satisfies
the external validation requirements.
