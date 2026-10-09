#!/usr/bin/env python3
"""AUNEYA INV-006 experimental Ed25519 attestation verifier.

Research-only. Does not issue tokens, rewards or transfers.
"""

import hashlib
import re
import subprocess
from pathlib import Path

DOMAIN = b"AUNEYA-WITNESS-ATTESTATION-V0.1\x00"
CHAIN_RE = re.compile(
    r"^auneya-(research|simulation|devnet|testnet)-"
    r"[a-z0-9-]+-v[0-9]+$"
)
WITNESS_RE = re.compile(r"^witness_[a-z0-9_-]{8,100}$")
HASH_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


class AttestationError(ValueError):
    pass


def _field(value: str) -> bytes:
    if not isinstance(value, str):
        raise AttestationError("field must be string")
    raw = value.encode("utf-8")
    if len(raw) > 65535:
        raise AttestationError("field too long")
    return len(raw).to_bytes(2, "big") + raw


def signing_message(
    chain_id: str,
    witness_id: str,
    payload_hash: str,
) -> bytes:
    if not isinstance(chain_id, str) or not CHAIN_RE.fullmatch(chain_id):
        raise AttestationError("invalid chain_id")
    if not isinstance(witness_id, str) or not WITNESS_RE.fullmatch(witness_id):
        raise AttestationError("invalid witness_id")
    if not isinstance(payload_hash, str) or not HASH_RE.fullmatch(payload_hash):
        raise AttestationError("invalid payload_hash")

    return (
        DOMAIN
        + _field(chain_id)
        + _field(witness_id)
        + _field(payload_hash)
    )


def hash_payload(payload: bytes) -> str:
    if not isinstance(payload, bytes):
        raise AttestationError("payload must be bytes")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def verify(
    public_key: Path,
    signature: Path,
    chain_id: str,
    witness_id: str,
    payload: bytes,
) -> bool:
    """Fail closed; caller supplies trusted key and expected context."""
    message = signing_message(
        chain_id, witness_id, hash_payload(payload)
    )

    for path in (public_key, signature):
        if path.is_symlink() or not path.is_file():
            return False

    import tempfile

    with tempfile.TemporaryDirectory() as temp:
        msg = Path(temp) / "message.bin"
        msg.write_bytes(message)

        result = subprocess.run(
            [
                "openssl", "pkeyutl", "-verify",
                "-pubin", "-inkey", str(public_key),
                "-sigfile", str(signature),
                "-rawin", "-in", str(msg),
            ],
            capture_output=True,
            check=False,
            timeout=15,
        )

    return result.returncode == 0
