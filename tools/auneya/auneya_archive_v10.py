#!/usr/bin/env python3

"""
AUNEYA/WVP v1.0

Transactional replay protection and evidence archive.

Authenticates pinned signed operator statements.
Does not prove the truth of those statements.

Offline, non-value research only.
No wallet or mainnet mutation.
"""

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import time
from urllib.parse import quote

import auneya_nightfall_challenge_v05 as v5
import auneya_registry_checkpoint_v06 as v6
import auneya_pinned_observation_v07 as v7
import auneya_archive_v09 as v9


MAX_CAPSULE = 3 * 1024 * 1024

FORMAT = "auneya-transactional-archive-v1.0"


class ArchiveError(ValueError):
    pass


def check_private_db(path, create=False):

    p = Path(path).absolute()

    if p.is_symlink():
        raise ArchiveError("database symlink refused")

    if p.exists():

        s = p.stat()

        if (
            not stat.S_ISREG(s.st_mode)
            or s.st_mode & 0o077
        ):
            raise ArchiveError(
                "database must be private regular file (0600)"
            )

    elif not create:
        raise ArchiveError("archive database does not exist")

    if not p.parent.is_dir():
        raise ArchiveError("archive directory missing")

    return p


def read_only(path):

    p = check_private_db(path)

    uri = (
        "file:"
        + quote(str(p), safe="/")
        + "?mode=ro"
    )

    return sqlite3.connect(
        uri,
        uri=True,
        timeout=5,
    )


def prepare(
    challenge,
    receipts,
    registry,
    seal,
    pin,
    now,
):

    if (
        not isinstance(receipts, list)
        or not 2 <= len(receipts) <= 16
    ):
        raise ArchiveError(
            "require 2 to 16 signed observations"
        )

    v5.check_challenge(challenge, now)

    locked, keys = v9.key_snapshot(
        registry,
        seal,
        pin,
    )

    for r in receipts:

        if (
            not isinstance(r, dict)
            or type(r.get("observed_at")) is not int
        ):
            raise ArchiveError(
                "invalid observation time"
            )

        if r["observed_at"] > now + 30:
            raise ArchiveError(
                "observation from the future"
            )

    ordered = sorted(
        receipts,
        key=lambda x: x["node_id"],
    )

    obj = {

        "format": v9.F,

        "seal": locked,

        "challenge": challenge,

        "receipts": ordered,

        "keys": {
            r["node_id"]: keys[r["node_id"]]
            for r in ordered
        },

        "report": v9.expected_report(
            challenge,
            ordered,
            pin,
        ),
    }

    # Reuse actual v0.9 signature validation.
    v9.inspect(obj, pin)

    raw = v6.canonical(obj)

    if len(raw) >= MAX_CAPSULE:
        raise ArchiveError("capsule size limit")

    current = v6.snapshot(registry)

    if any(
        current[k] != locked[k]
        for k in ("nodes", "events")
    ):
        raise ArchiveError(
            "registry changed since checkpoint"
        )

    return obj, raw


def capture(
    challenge,
    receipts,
    registry,
    seal,
    pin,
    ledger,
    now=None,
    before_commit=None,
):

    """
    Replay entries and evidence capsule are committed
    in one SQLite transaction.

    before_commit is a test-only failure hook.
    """

    ledger = check_private_db(
        ledger,
        create=True,
    )

    v7.ensure_not_input(
        ledger,
        registry,
        seal,
    )

    if now is None:
        now = int(time.time())

    obj, raw = prepare(
        challenge,
        receipts,
        registry,
        seal,
        pin,
        now,
    )

    report = obj["report"]

    old_mask = os.umask(0o077)

    try:

        with closing(
            sqlite3.connect(
                str(ledger),
                timeout=5,
            )
        ) as db:

            db.execute(
                "PRAGMA busy_timeout=5000"
            )

            db.execute(
                "PRAGMA journal_mode=DELETE"
            )

            db.execute(
                "PRAGMA synchronous=FULL"
            )

            if ledger.stat().st_mode & 0o077:
                raise ArchiveError(
                    "database permissions changed"
                )

            # Existing v0.5-compatible replay table.
            db.execute(
                "CREATE TABLE IF NOT EXISTS receipts("
                "nonce TEXT NOT NULL,"
                "node_id TEXT NOT NULL,"
                "receipt_hash TEXT NOT NULL,"
                "PRIMARY KEY(nonce,node_id))"
            )

            # Durable evidence capsules.
            db.execute(
                "CREATE TABLE IF NOT EXISTS "
                "archive_capsules_v10("
                "evidence_sha256 TEXT PRIMARY KEY,"
                "external_pin TEXT NOT NULL,"
                "capsule BLOB NOT NULL)"
            )

            # Schema bootstrap contains no evidence.
            db.commit()

            db.execute("BEGIN IMMEDIATE")

            try:

                for r in obj["receipts"]:

                    receipt_hash = hashlib.sha256(
                        v5.canonical(r)
                    ).hexdigest()

                    db.execute(
                        "INSERT INTO receipts "
                        "VALUES (?,?,?)",
                        (
                            challenge["nonce"],
                            r["node_id"],
                            receipt_hash,
                        ),
                    )

                db.execute(
                    "INSERT INTO archive_capsules_v10 "
                    "VALUES (?,?,?)",
                    (
                        report["evidence_sha256"],
                        pin,
                        sqlite3.Binary(raw),
                    ),
                )

                if before_commit is not None:
                    before_commit()

                # Both receipt and capsule become durable.
                db.commit()

            except BaseException:

                db.rollback()
                raise

    except sqlite3.IntegrityError as exc:

        raise ArchiveError(
            "duplicate, replayed or malformed archive"
        ) from exc

    finally:

        os.umask(old_mask)

    return {

        "storage": FORMAT,

        "result": "ATOMIC_ARCHIVE_COMMITTED",

        "evidence_sha256":
            report["evidence_sha256"],

        "operator_count":
            report["operator_count"],

        "consensus_validated": False,

        "independent_operators_proven": False,

        "non_value_research_only": True,
    }


def inspect_db(
    ledger,
    evidence_sha256,
    pin,
):

    if (
        not isinstance(evidence_sha256, str)
        or len(evidence_sha256) != 64
        or any(
            c not in "0123456789abcdef"
            for c in evidence_sha256
        )
    ):
        raise ArchiveError(
            "invalid evidence digest"
        )

    with closing(read_only(ledger)) as db:

        row = db.execute(
            "SELECT external_pin, capsule "
            "FROM archive_capsules_v10 "
            "WHERE evidence_sha256=?",
            (evidence_sha256,),
        ).fetchone()

        if row is None:
            raise ArchiveError("archive not found")

        stored_pin, raw = row

        if (
            stored_pin != pin
            or not isinstance(raw, bytes)
            or len(raw) >= MAX_CAPSULE
        ):
            raise ArchiveError(
                "pin mismatch or oversized archive"
            )

        obj = json.loads(
            raw,
            object_pairs_hook=v5.pairs,
            parse_constant=lambda x: (
                _ for _ in ()
            ).throw(
                ArchiveError("nonfinite JSON")
            ),
        )

        if raw != v6.canonical(obj):
            raise ArchiveError(
                "noncanonical archived capsule"
            )

        # Historical signature verification.
        finding = v9.inspect(obj, pin)

        if (
            finding["evidence_sha256"]
            != evidence_sha256
        ):
            raise ArchiveError(
                "evidence commitment mismatch"
            )

        # Verify archive/replay consistency.
        for r in obj["receipts"]:

            found = db.execute(
                "SELECT receipt_hash "
                "FROM receipts "
                "WHERE nonce=? AND node_id=?",
                (
                    obj["challenge"]["nonce"],
                    r["node_id"],
                ),
            ).fetchone()

            expected = hashlib.sha256(
                v5.canonical(r)
            ).hexdigest()

            if found != (expected,):
                raise ArchiveError(
                    "archive-replay consistency failure"
                )

    return obj, finding


def export(
    ledger,
    digest,
    pin,
    output,
):

    out = Path(output).absolute()
    source = Path(ledger).absolute()

    if (
        out == source
        or (
            out.exists()
            and source.exists()
            and os.path.samefile(out, source)
        )
    ):
        raise ArchiveError(
            "output aliases archive database"
        )

    obj, finding = inspect_db(
        ledger,
        digest,
        pin,
    )

    # Exclusive write + fsync from v0.6.
    v6.write_new(out, obj)

    return finding


def main():

    p = argparse.ArgumentParser(
        description=__doc__
    )

    sub = p.add_subparsers(
        dest="action",
        required=True,
    )

    a = sub.add_parser("capture")

    for flag in (
        "challenge",
        "registry",
        "seal",
        "expected-sha256",
        "ledger",
    ):
        a.add_argument(
            "--" + flag,
            required=True,
        )

    a.add_argument(
        "--receipt",
        action="append",
        required=True,
    )

    for action in (
        "inspect",
        "export",
    ):

        b = sub.add_parser(action)

        for flag in (
            "ledger",
            "evidence-sha256",
            "expected-sha256",
        ):
            b.add_argument(
                "--" + flag,
                required=True,
            )

        if action == "export":
            b.add_argument(
                "--out",
                required=True,
            )

    x = p.parse_args()

    try:

        if x.action == "capture":

            result = capture(
                v5.read(x.challenge),
                [
                    v5.read(r)
                    for r in x.receipt
                ],
                x.registry,
                x.seal,
                x.expected_sha256,
                x.ledger,
            )

        elif x.action == "inspect":

            _, result = inspect_db(
                x.ledger,
                x.evidence_sha256,
                x.expected_sha256,
            )

        else:

            result = export(
                x.ledger,
                x.evidence_sha256,
                x.expected_sha256,
                x.out,
            )

        print(
            json.dumps(
                result,
                sort_keys=True,
            )
        )

    except (
        ArchiveError,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
        OSError,
        sqlite3.Error,
        RecursionError,
    ) as exc:

        p.exit(
            2,
            "FAIL-CLOSED: " + str(exc) + "\n",
        )


if __name__ == "__main__":
    main()
