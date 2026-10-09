#!/usr/bin/env python3
"""Experimental AUNEYA witness-proof verification adapter."""

import copy
import hashlib
import json
import re
from pathlib import Path

from auneya_attestation_binding import (
    AttestationError,
    verify,
)

HASH_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


class ProofError(ValueError):
    pass


def canonical_bytes(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def unsigned_payload(proof):
    if not isinstance(proof, dict):
        raise ProofError("proof must be an object")

    obj = copy.deepcopy(proof)
    integrity = obj.get("integrity")

    if not isinstance(integrity, dict):
        raise ProofError("missing integrity")

    integrity.pop("signature", None)
    integrity.pop("signature_algorithm", None)
    integrity.pop("signature_status", None)
    integrity.pop("proof_hash", None)

    return canonical_bytes(obj)


def payload_hash(proof):
    raw = unsigned_payload(proof)
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def verify_proof(
    proof,
    expected_chain_id,
    trusted_witness_id,
    trusted_public_key,
    signature_path,
):
    """Fail closed using externally trusted verification context."""

    if not isinstance(proof, dict):
        return False

    if proof.get("schema_version") != "auneya-witness-proof-v0.1":
        return False

    witness = proof.get("witness")
    integrity = proof.get("integrity")

    if not isinstance(witness, dict):
        return False

    if not isinstance(integrity, dict):
        return False

    if witness.get("witness_id") != trusted_witness_id:
        return False

    if integrity.get("signature_status") != "signed":
        return False

    if integrity.get("signature_algorithm") != "ed25519":
        return False

    # Legacy inline signatures are deliberately unsupported.
    # The signature is supplied as a separate trusted input.
    if "signature" in integrity:
        return False

    try:
        raw = unsigned_payload(proof)
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()

        if not HASH_RE.fullmatch(digest):
            return False

        if integrity.get("proof_hash") != digest:
            return False

        return verify(
            Path(trusted_public_key),
            Path(signature_path),
            expected_chain_id,
            trusted_witness_id,
            raw,
        )

    except (
        AttestationError,
        ProofError,
        OSError,
        TypeError,
        ValueError,
        RuntimeError,
    ):
        return False
