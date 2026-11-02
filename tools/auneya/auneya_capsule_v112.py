#!/usr/bin/env python3

"""
AUNEYA/WVP v1.12

Portable Authenticated Quorum Evidence.

Security properties:

- Bounded canonical evidence capsules.
- No private signing keys in exports.
- Separately configured trust anchors.
- Reuse of v1.11 cryptographic verification.
- Atomic recipient high-water storage.
- Stale checkpoint rejection.
- Signed predecessor continuity.
- Same-height anchor conflict rejection.
- No monetary or network activation.

Research implementation only.
"""

import argparse
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

import auneya_peer_gate_v16 as gate
import auneya_quorum_v111 as quorum

FORMAT = "auneya-portable-quorum-capsule-v1.12"
FLOOR = "auneya-recipient-highwater-v1.12"
VERDICT = "wvp-auneya-portable-capsule-verdict-v1.12"

LIMIT = 4 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exact(value, keys):
    need(
        type(value) is dict
        and set(value) == set(keys),
        "Unexpected or missing object keys"
    )


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_bytes(raw):
    need(
        raw.endswith(b"\n")
        and raw.count(b"\n") == 1,
        "noncanonical JSON framing: exactly one LF-terminated object required"
    )

    obj = gate.strict_json(raw[:-1])

    need(
        type(obj) is dict
        and gate.canonical(obj) + b"\n" == raw,
        "Noncanonical JSON"
    )

    return obj


def public_read(path, limit=LIMIT):
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
    )

    fd = os.open(os.fspath(path), flags)

    try:
        info = os.fstat(fd)

        need(
            stat.S_ISREG(info.st_mode),
            "Not a regular file"
        )

        need(
            info.st_size <= limit,
            "File exceeds resource limit"
        )

        with os.fdopen(os.dup(fd), "rb") as stream:
            raw = stream.read(limit + 1)

        need(
            len(raw) <= limit,
            "File exceeds resource limit"
        )

        return raw

    finally:
        os.close(fd)


def encoded(raw):
    return base64.b64encode(raw).decode("ascii")


def decoded(value, limit):
    need(
        type(value) is str
        and len(value) <= ((limit + 2) // 3) * 4,
        "Invalid or oversized base64"
    )

    try:
        raw = base64.b64decode(
            value,
            validate=True
        )

    except (ValueError, base64.binascii.Error) as exc:
        raise ValueError("Invalid base64") from exc

    need(
        len(raw) <= limit
        and encoded(raw) == value,
        "Noncanonical or oversized base64"
    )

    return raw


def write_private(path, raw):
    path = Path(path)

    fd = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600
    )

    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def capture_bundle(filename):
    path = Path(filename).absolute()

    record = quorum.load(path)

    quorum.exact_keys(
        record,
        ("format", "anchor", "receipts")
    )

    need(
        record["format"] == quorum.BUNDLE_FORMAT,
        "Wrong source bundle format"
    )

    anchor_path = quorum.path_for(
        path.parent,
        record["anchor"]
    )

    anchor_raw = gate.read_private(
        anchor_path,
        1024 * 1024
    )

    items = []

    need(
        type(record["receipts"]) is list
        and 1 <= len(record["receipts"]) <= quorum.MAX_KEEPERS,
        "Invalid receipt count"
    )

    for item in record["receipts"]:
        quorum.exact_keys(
            item,
            ("pin", "path")
        )

        receipt_path = quorum.path_for(
            path.parent,
            item["path"]
        )

        raw = gate.read_private(
            receipt_path,
            16 * 1024
        )

        items.append({
            "pin": item["pin"],
            "payload_b64": encoded(raw)
        })

    need(
        len({item["pin"] for item in items})
        == len(items),
        "Duplicate keeper"
    )

    return {
        "anchor_b64": encoded(anchor_raw),
        "receipts": sorted(
            items,
            key=lambda item: item["pin"]
        )
    }


def assemble_bundle(directory, label, record):
    exact(
        record,
        ("anchor_b64", "receipts")
    )

    receipts = record["receipts"]

    need(
        type(receipts) is list
        and 1 <= len(receipts) <= quorum.MAX_KEEPERS,
        "Invalid portable receipt list"
    )

    root = Path(directory)

    anchor_path = root / (
        label + "-anchor.json"
    )

    write_private(
        anchor_path,
        decoded(
            record["anchor_b64"],
            1024 * 1024
        )
    )

    source = []
    pins = []

    for index, obj in enumerate(receipts):
        exact(
            obj,
            ("pin", "payload_b64")
        )

        pin = obj["pin"]

        need(
            type(pin) is str
            and gate.HEX.fullmatch(pin),
            "Invalid keeper pin"
        )

        path = root / (
            f"{label}-keeper-{index}.json"
        )

        write_private(
            path,
            decoded(
                obj["payload_b64"],
                16 * 1024
            )
        )

        source.append({
            "pin": pin,
            "path": str(path)
        })

        pins.append(pin)

    need(
        pins == sorted(set(pins)),
        "Keeper pins must be unique and sorted"
    )

    bundle_path = root / (
        label + "-bundle.json"
    )

    bundle = {
        "format": quorum.BUNDLE_FORMAT,
        "anchor": str(anchor_path),
        "receipts": source
    }

    write_private(
        bundle_path,
        gate.canonical(bundle) + b"\n"
    )

    return bundle_path


def public_verdict(report, capsule_sha256, floor_status):
    return {
        "format": VERDICT,
        "status":
            "AUTHENTICATED_PORTABLE_QUORUM_RESEARCH_EVIDENCE",
        "chain_id": report["chain_id"],
        "sequence": report["sequence"],
        "anchor_sha256": report["anchor_sha256"],
        "keeper_count": report["keeper_count"],
        "required_quorum": report["required_quorum"],
        "capsule_sha256": capsule_sha256,
        "floor_status": floor_status,
        "signatures_verified": True,
        "independent_devices_proven": False,
        "external_retention_proven": False,
        "global_latest_proven": False,
        "audit_completed": False,
        "economic_activation": False,
        "non_value_research_only": True
    }


def export_capsule(
    trust,
    bundle,
    output,
    previous=None
):
    report = quorum.run(
        trust,
        bundle,
        previous
    )

    body = {
        "format": FORMAT,
        "chain_id": report["chain_id"],
        "sequence": report["sequence"],
        "anchor_sha256": report["anchor_sha256"],
        "quorum_report_sha256":
            sha(gate.canonical(report)),
        "current": capture_bundle(bundle),
        "previous":
            capture_bundle(previous)
            if previous else None
    }

    raw = gate.canonical(body) + b"\n"

    need(
        len(raw) <= LIMIT,
        "Capsule exceeds resource budget"
    )

    write_private(output, raw)

    return public_verdict(
        report,
        sha(raw),
        "not_evaluated"
    )


def update_floor(
    floor_path,
    report,
    raw_trust,
    capsule_sha,
    previous_hash
):
    path = Path(floor_path).absolute()
    parent = path.parent

    need(
        parent.is_dir()
        and not parent.is_symlink(),
        "Floor directory must exist and not be symlinked"
    )

    need(
        stat.S_IMODE(parent.stat().st_mode)
        & 0o077 == 0,
        "Floor directory must be private: chmod 700"
    )

    identity = sha(raw_trust)

    record = {
        "format": FLOOR,
        "chain_id": report["chain_id"],
        "trust_sha256": identity,
        "sequence": report["sequence"],
        "anchor_sha256": report["anchor_sha256"],
        "last_capsule_sha256": capsule_sha
    }

    lockpath = path.with_name(
        path.name + ".lock"
    )

    lockfd = os.open(
        lockpath,
        os.O_CREAT
        | os.O_RDWR
        | getattr(os, "O_NOFOLLOW", 0),
        0o600
    )

    try:
        need(
            stat.S_ISREG(
                os.fstat(lockfd).st_mode
            ),
            "Invalid floor lock"
        )

        fcntl.flock(
            lockfd,
            fcntl.LOCK_EX
        )

        if path.exists() or path.is_symlink():
            before = strict_bytes(
                public_read(path, 4096)
            )

            exact(
                before,
                tuple(record)
            )

            need(
                before["format"] == FLOOR
                and before["chain_id"] == record["chain_id"]
                and before["trust_sha256"] == identity,
                "Different floor chain or trust policy"
            )

            need(
                type(before["sequence"]) is int
                and before["sequence"] >= 1
                and type(before["anchor_sha256"]) is str
                and gate.HEX.fullmatch(
                    before["anchor_sha256"]
                ),
                "Invalid high-water record"
            )

            if record["sequence"] == before["sequence"]:
                need(
                    record["anchor_sha256"]
                    == before["anchor_sha256"],
                    "EQUIVOCATION: conflicting same-height anchor"
                )

                return "unchanged"

            need(
                record["sequence"]
                == before["sequence"] + 1,
                "STALE or skipped high-water sequence"
            )

            need(
                previous_hash
                == before["anchor_sha256"],
                "External high-water predecessor mismatch"
            )

            status = "advanced"

        else:
            need(
                record["sequence"] == 1,
                "Floor bootstrap requires genesis sequence 1"
            )

            status = "initialized"

        fd, temp = tempfile.mkstemp(
            prefix=".auneya-floor-",
            dir=parent
        )

        try:
            with os.fdopen(fd, "wb") as out:
                out.write(
                    gate.canonical(record)
                    + b"\n"
                )

                out.flush()
                os.fsync(out.fileno())

            os.replace(
                temp,
                path
            )

            dfd = os.open(
                parent,
                os.O_RDONLY
            )

            try:
                os.fsync(dfd)

            finally:
                os.close(dfd)

        finally:
            if os.path.exists(temp):
                os.unlink(temp)

        return status

    finally:
        os.close(lockfd)


def verify_capsule(
    trust,
    capsule,
    floor=None
):
    raw = public_read(capsule)
    obj = strict_bytes(raw)

    exact(
        obj,
        (
            "format",
            "chain_id",
            "sequence",
            "anchor_sha256",
            "quorum_report_sha256",
            "current",
            "previous"
        )
    )

    need(
        obj["format"] == FORMAT,
        "Wrong capsule format"
    )

    need(
        type(obj["chain_id"]) is str
        and gate.CHAIN.fullmatch(
            obj["chain_id"]
        ),
        "Invalid chain identity"
    )

    need(
        type(obj["sequence"]) is int
        and obj["sequence"] >= 1,
        "Invalid sequence"
    )

    for field in (
        "anchor_sha256",
        "quorum_report_sha256"
    ):
        need(
            type(obj[field]) is str
            and gate.HEX.fullmatch(
                obj[field]
            ),
            "Invalid capsule digest"
        )

    with tempfile.TemporaryDirectory(
        prefix="auneya-v112-"
    ) as td:

        current = assemble_bundle(
            td,
            "current",
            obj["current"]
        )

        previous = (
            assemble_bundle(
                td,
                "previous",
                obj["previous"]
            )
            if obj["previous"] is not None
            else None
        )

        result = quorum.run(
            trust,
            current,
            previous
        )

        need(
            (
                result["chain_id"],
                result["sequence"],
                result["anchor_sha256"]
            )
            ==
            (
                obj["chain_id"],
                obj["sequence"],
                obj["anchor_sha256"]
            ),
            "Signed content differs from capsule metadata"
        )

        need(
            sha(gate.canonical(result))
            == obj["quorum_report_sha256"],
            "WVP report commitment differs"
        )

        previous_hash = None

        if previous:
            policy, anchor_public, members = (
                quorum.read_trust(trust)
            )

            prior = quorum.verify_bundle(
                previous,
                policy,
                anchor_public,
                members
            )

            previous_hash = prior[1]

    status = "not_configured"

    if floor is not None:
        status = update_floor(
            floor,
            result,
            gate.read_private(
                trust,
                32768
            ),
            sha(raw),
            previous_hash
        )

    return public_verdict(
        result,
        sha(raw),
        status
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True
    )

    exporter = commands.add_parser(
        "export"
    )

    exporter.add_argument(
        "--trust",
        required=True
    )

    exporter.add_argument(
        "--bundle",
        required=True
    )

    exporter.add_argument(
        "--previous"
    )

    exporter.add_argument(
        "--output",
        required=True
    )

    verifier = commands.add_parser(
        "verify"
    )

    verifier.add_argument(
        "--trust",
        required=True
    )

    verifier.add_argument(
        "--capsule",
        required=True
    )

    verifier.add_argument(
        "--floor"
    )

    args = parser.parse_args()

    try:
        if args.command == "export":
            result = export_capsule(
                args.trust,
                args.bundle,
                args.output,
                args.previous
            )

        else:
            result = verify_capsule(
                args.trust,
                args.capsule,
                args.floor
            )

        sys.stdout.buffer.write(
            gate.canonical(result)
            + b"\n"
        )

    except (ValueError, OSError) as exc:
        parser.exit(
            2,
            f"REJECTED: {exc}\n"
        )


if __name__ == "__main__":
    main()
