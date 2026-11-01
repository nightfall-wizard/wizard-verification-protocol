#!/usr/bin/env python3

"""
AUNEYA v1.11

Authenticated Multi-Keeper Quorum
and Equivocation Detection.

Offline research implementation.

Reuses:
- AUNEYA v1.6 canonical encoding
- AUNEYA v1.9 signed anchors
- AUNEYA v1.10 signed witness receipts

Security model:
- Fail closed
- Explicit independent key pins
- Authenticated signed evidence
- Distinct signer identities
- Bounded keeper count
- Deterministic verification
- Signed predecessor continuity
- Detection of supplied equivocation

This does not prove:
- Physical device independence
- External immutable retention
- Global latest checkpoint
- Sybil resistance
- Consensus
- Mainnet readiness
- Independent security audit

No economic activation.
"""

import argparse
from pathlib import Path
import sys

import auneya_anchor_v19 as anchor
import auneya_peer_gate_v16 as gate
import auneya_witness_v110 as witness


TRUST_FORMAT = "auneya-quorum-trust-v1.11"

BUNDLE_FORMAT = "auneya-quorum-evidence-v1.11"

REPORT_FORMAT = "wvp-auneya-quorum-verdict-v1.11"

MAX_CONFIG = 32768

MAX_KEEPERS = 16


class QuorumError(ValueError):
    pass


def need(condition, message):

    if not condition:
        raise QuorumError(message)


def load(path):

    raw = gate.read_private(
        path,
        MAX_CONFIG
    )

    need(
        raw.endswith(b"\n")
        and raw.count(b"\n") == 1,
        "configuration must use canonical JSON framing"
    )

    obj = gate.strict_json(
        raw[:-1]
    )

    need(
        type(obj) is dict
        and gate.canonical(obj) + b"\n" == raw,
        "noncanonical or invalid configuration"
    )

    return obj


def exact_keys(obj, names):

    need(
        type(obj) is dict
        and set(obj) == set(names),
        "unknown or missing JSON fields"
    )


def path_for(base, value):

    need(
        type(value) is str
        and 0 < len(value) < 1024,
        "invalid file path"
    )

    path = Path(value)

    need(
        ".." not in path.parts,
        "path traversal refused"
    )

    if path.is_absolute():
        return path

    return base / path


def read_trust(filename):

    path = Path(filename).absolute()

    obj = load(path)

    exact_keys(
        obj,
        (
            "format",
            "chain_id",
            "anchor_public",
            "anchor_pin",
            "keepers",
            "threshold"
        )
    )

    need(
        obj["format"] == TRUST_FORMAT,
        "incorrect trust format"
    )

    need(
        type(obj["chain_id"]) is str
        and gate.CHAIN.fullmatch(
            obj["chain_id"]
        ) is not None,
        "incorrect research chain identity"
    )

    threshold = obj["threshold"]

    keepers = obj["keepers"]

    need(
        type(threshold) is int
        and 2 <= threshold <= MAX_KEEPERS,
        "invalid quorum threshold"
    )

    need(
        type(keepers) is list
        and threshold <= len(keepers) <= MAX_KEEPERS,
        "invalid keeper population"
    )

    anchor_pin = obj["anchor_pin"]

    need(
        type(anchor_pin) is str
        and gate.HEX.fullmatch(
            anchor_pin
        ) is not None,
        "invalid anchor signer fingerprint"
    )

    anchor_public = path_for(
        path.parent,
        obj["anchor_public"]
    )

    anchor.check_pin(
        anchor_public,
        anchor_pin
    )

    members = {}

    for member in keepers:

        exact_keys(
            member,
            ("pin", "public")
        )

        pin = member["pin"]

        need(
            type(pin) is str
            and gate.HEX.fullmatch(pin) is not None,
            "invalid keeper fingerprint"
        )

        need(
            pin != anchor_pin,
            "anchor and keeper identities must differ"
        )

        need(
            pin not in members,
            "duplicate keeper identity"
        )

        public = path_for(
            path.parent,
            member["public"]
        )

        anchor.check_pin(
            public,
            pin
        )

        members[pin] = public

    return obj, anchor_public, members


def verify_bundle(
    filename,
    trust,
    anchor_public,
    members
):

    path = Path(filename).absolute()

    bundle = load(path)

    exact_keys(
        bundle,
        (
            "format",
            "anchor",
            "receipts"
        )
    )

    need(
        bundle["format"] == BUNDLE_FORMAT,
        "incorrect evidence format"
    )

    receipts = bundle["receipts"]

    need(
        type(receipts) is list
        and 1 <= len(receipts) <= MAX_KEEPERS,
        "invalid receipt list"
    )

    anchor_file = path_for(
        path.parent,
        bundle["anchor"]
    )

    trusted_anchor_key = anchor.check_pin(
        anchor_public,
        trust["anchor_pin"]
    )

    anchor_body, anchor_hash = anchor.load_anchor(
        anchor_file,
        trusted_anchor_key,
        trust["anchor_pin"]
    )

    need(
        anchor_body["chain_id"] == trust["chain_id"],
        "wrong research chain"
    )

    verified = {}

    for member in receipts:

        exact_keys(
            member,
            ("pin", "path")
        )

        pin = member["pin"]

        need(
            type(pin) is str
            and pin in members,
            "unknown keeper identity"
        )

        need(
            pin not in verified,
            "duplicate keeper identity"
        )

        receipt_file = path_for(
            path.parent,
            member["path"]
        )

        result = witness.verify(
            anchor_file,
            receipt_file,
            anchor_public,
            trust["anchor_pin"],
            members[pin],
            pin
        )

        trusted_keeper_key = anchor.check_pin(
            members[pin],
            pin
        )

        receipt_body, receipt_hash, _ = (
            witness.inspect_receipt(
                receipt_file,
                trusted_keeper_key,
                pin
            )
        )

        need(
            result["anchor_sha256"] == anchor_hash,
            "inconsistent anchor commitment"
        )

        need(
            result["receipt_sha256"] == receipt_hash,
            "inconsistent receipt commitment"
        )

        need(
            receipt_body["chain_id"] == trust["chain_id"],
            "receipt chain mismatch"
        )

        verified[pin] = {
            "body": receipt_body,
            "hash": receipt_hash,
            "receipt_path": receipt_file
        }

    need(
        len(verified) >= trust["threshold"],
        "insufficient signed quorum"
    )

    return (
        anchor_body,
        anchor_hash,
        verified
    )


def check_successor(before, after):

    old_body, old_hash, old_receipts = before

    body, _, receipts = after

    need(
        body["chain_id"] == old_body["chain_id"],
        "chain migration without authorization"
    )

    need(
        body["sequence"] == old_body["sequence"] + 1,
        "anchor rollback or skipped checkpoint"
    )

    need(
        body["previous_sha256"] == old_hash,
        "anchor fork or predecessor mismatch"
    )

    need(
        body["message_count"] > old_body["message_count"],
        "non-monotonic evidence height"
    )

    need(
        set(old_receipts) == set(receipts),
        "keeper membership transition requires review"
    )

    for pin, entry in receipts.items():

        previous = old_receipts[pin]

        current_body = entry["body"]

        old_receipt_body = previous["body"]

        need(
            current_body["sequence"]
            == old_receipt_body["sequence"] + 1,
            "keeper receipt rollback or skipped height"
        )

        need(
            current_body["previous_receipt_sha256"]
            == previous["hash"],
            "keeper receipt fork or predecessor mismatch"
        )

        need(
            current_body["previous_anchor_sha256"]
            == old_hash,
            "keeper anchor predecessor mismatch"
        )


def check_equivocation(left, right):

    body_a, hash_a, receipts_a = left

    body_b, hash_b, receipts_b = right

    need(
        body_a["chain_id"] == body_b["chain_id"],
        "comparison chain mismatch"
    )

    need(
        body_a["sequence"] == body_b["sequence"],
        "equivocation comparison requires same height"
    )

    need(
        hash_a == hash_b,
        "EQUIVOCATION: conflicting signed anchor"
    )

    common = receipts_a.keys() & receipts_b.keys()

    for pin in common:

        need(
            receipts_a[pin]["hash"]
            == receipts_b[pin]["hash"],
            "EQUIVOCATION: conflicting keeper receipt"
        )


def run(
    trust_path,
    current_path,
    previous_path=None,
    compare_path=None,
    compare_previous_path=None
):

    trust, anchor_public, members = read_trust(
        trust_path
    )

    current = verify_bundle(
        current_path,
        trust,
        anchor_public,
        members
    )

    anchor_body, anchor_hash, receipts = current

    if anchor_body["sequence"] > 1:

        need(
            previous_path is not None,
            "non-genesis evidence requires previous signed bundle"
        )

    if previous_path:

        previous = verify_bundle(
            previous_path,
            trust,
            anchor_public,
            members
        )

        check_successor(
            previous,
            current
        )

    if compare_path:

        other = verify_bundle(
            compare_path,
            trust,
            anchor_public,
            members
        )

        if other[0]["sequence"] > 1:

            need(
                compare_previous_path is not None,
                "comparison above genesis requires previous signed bundle"
            )

        if compare_previous_path:

            other_previous = verify_bundle(
                compare_previous_path,
                trust,
                anchor_public,
                members
            )

            check_successor(
                other_previous,
                other
            )

        check_equivocation(
            current,
            other
        )

    elif compare_previous_path:

        raise QuorumError(
            "compare-previous requires compare"
        )

    report = {
        "format": REPORT_FORMAT,

        "status":
            "AUTHENTICATED_MULTI_KEEPER_RESEARCH_EVIDENCE",

        "chain_id":
            anchor_body["chain_id"],

        "sequence":
            anchor_body["sequence"],

        "anchor_sha256":
            anchor_hash,

        "message_count":
            anchor_body["message_count"],

        "keeper_count":
            len(receipts),

        "required_quorum":
            trust["threshold"],

        "keeper_receipt_sha256": [
            {
                "pin": pin,
                "sha256": receipts[pin]["hash"]
            }

            for pin in sorted(receipts)
        ],

        "signatures_verified": True,

        "independent_devices_proven": False,

        "external_retention_proven": False,

        "latest_global_highwater_proven": False,

        "network_consensus_proven": False,

        "audit_completed": False,

        "economic_activation": False,

        "non_value_research_only": True
    }

    return report


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--trust",
        required=True
    )

    parser.add_argument(
        "--bundle",
        required=True
    )

    parser.add_argument(
        "--previous"
    )

    parser.add_argument(
        "--compare"
    )

    parser.add_argument(
        "--compare-previous"
    )

    parser.add_argument(
        "--output"
    )

    args = parser.parse_args()

    try:

        report = run(
            args.trust,
            args.bundle,
            args.previous,
            args.compare,
            args.compare_previous
        )

        raw = gate.canonical(report) + b"\n"

        if args.output:

            witness.put_file_new(
                args.output,
                raw
            )

        sys.stdout.buffer.write(raw)

    except (ValueError, OSError) as exc:

        parser.exit(
            2,
            "FAIL-CLOSED: " + str(exc) + "\n"
        )


if __name__ == "__main__":
    main()
