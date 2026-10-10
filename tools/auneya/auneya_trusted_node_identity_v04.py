#!/usr/bin/env python3
"""AUNEYA Trusted Node Identity v0.4, local research only.

An operator-pinned SQLite Ed25519 identity registry,
explicit dual-signature rotation, irreversible revocation,
and a v0.3 sender wrapper. No mainnet.
"""

import argparse
import base64
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile

import auneya_authenticated_ack_v03 as ack

PROTO = "auneya-trusted-node-identity-v0.4"
DOMAIN = b"AUNEYA-RESEARCH-NODE-IDENTITY-V0.4\x00"
ED25519_SPKI = bytes.fromhex(
    "302a300506032b6570032100"
)
HEX128 = re.compile(r"^[0-9a-f]{128}$")
MAX_EVENT = 8192


class IdentityError(ValueError):
    pass


def check_node(node):
    if (
        not isinstance(node, str)
        or not ack.NODE_RE.fullmatch(node)
    ):
        raise IdentityError("invalid node identity")
    return node


def key_der(path):
    path = ack.require_regular_key(path)

    p = subprocess.run(
        [
            "openssl", "pkey", "-pubin",
            "-in", str(path), "-outform", "DER",
        ],
        capture_output=True,
        timeout=15,
    )

    if (
        p.returncode
        or len(p.stdout) != 44
        or not p.stdout.startswith(ED25519_SPKI)
    ):
        raise IdentityError(
            "public key must be Ed25519 SPKI"
        )

    return p.stdout


def check_der(der):
    if (
        not isinstance(der, bytes)
        or len(der) != 44
        or not der.startswith(ED25519_SPKI)
    ):
        raise IdentityError(
            "invalid Ed25519 SPKI"
        )

    return der


def fingerprint(der):
    return hashlib.sha256(
        check_der(der)
    ).hexdigest()


def key_pem(der):
    encoded = base64.b64encode(
        check_der(der)
    ).decode("ascii")

    return (
        "-----BEGIN PUBLIC KEY-----\n"
        + encoded
        + "\n-----END PUBLIC KEY-----\n"
    ).encode("ascii")


def sign(private, body):
    private = ack.require_regular_key(private)

    if private.stat().st_mode & 0o077:
        raise IdentityError(
            "private key requires chmod 600"
        )

    with tempfile.TemporaryDirectory(
        prefix="auneya-v04-sign-"
    ) as tmp:

        msg = Path(tmp) / "msg"
        sig = Path(tmp) / "sig"

        msg.write_bytes(
            DOMAIN + ack.canonical(body)
        )

        p = subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-sign",
                "-inkey",
                str(private),
                "-rawin",
                "-in",
                str(msg),
                "-out",
                str(sig),
            ],
            capture_output=True,
            timeout=15,
        )

        if p.returncode:
            raise IdentityError(
                "identity signing failed"
            )

        raw = sig.read_bytes()

        if len(raw) != 64:
            raise IdentityError(
                "invalid identity signature length"
            )

        return raw.hex()


def verify(der, body, signature):
    if (
        not isinstance(signature, str)
        or not HEX128.fullmatch(signature)
    ):
        return False

    try:
        with tempfile.TemporaryDirectory(
            prefix="auneya-v04-verify-"
        ) as tmp:

            pub = Path(tmp) / "pub.pem"
            msg = Path(tmp) / "msg"
            sig = Path(tmp) / "sig"

            pub.write_bytes(
                key_pem(der)
            )

            msg.write_bytes(
                DOMAIN + ack.canonical(body)
            )

            sig.write_bytes(
                bytes.fromhex(signature)
            )

            p = subprocess.run(
                [
                    "openssl",
                    "pkeyutl",
                    "-verify",
                    "-pubin",
                    "-inkey",
                    str(pub),
                    "-sigfile",
                    str(sig),
                    "-rawin",
                    "-in",
                    str(msg),
                ],
                capture_output=True,
                timeout=15,
            )

            return p.returncode == 0

    except (
        ValueError,
        TypeError,
        OSError,
        subprocess.TimeoutExpired,
    ):
        return False


def database(path, create=False):
    path = Path(path)

    if path.is_symlink():
        raise IdentityError(
            "identity database symlink forbidden"
        )

    if not create and not path.is_file():
        raise IdentityError(
            "uninitialized identity registry"
        )

    if path.exists():
        if (
            not path.is_file()
            or path.stat().st_mode & 0o077
        ):
            raise IdentityError(
                "identity database must be "
                "a private regular file (0600)"
            )

    if create:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    old_umask = os.umask(0o077)

    try:
        db = sqlite3.connect(
            str(path),
            timeout=5,
        )

        db.execute(
            "PRAGMA busy_timeout=5000"
        )

        db.execute(
            "PRAGMA journal_mode=WAL"
        )

        db.execute(
            "PRAGMA synchronous=FULL"
        )

        db.execute(
            "CREATE TABLE IF NOT EXISTS nodes ("
            "node_id TEXT PRIMARY KEY, "
            "epoch INTEGER NOT NULL CHECK(epoch>=0), "
            "fingerprint TEXT NOT NULL, "
            "public_der BLOB NOT NULL, "
            "state TEXT NOT NULL "
            "CHECK(state IN ('active','revoked')))"
        )

        db.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "node_id TEXT NOT NULL, "
            "epoch INTEGER NOT NULL, "
            "event_digest TEXT NOT NULL, "
            "kind TEXT NOT NULL, "
            "PRIMARY KEY(node_id,epoch))"
        )

        db.commit()

        if path.stat().st_mode & 0o077:
            raise IdentityError(
                "registry filesystem does not "
                "enforce private permissions"
            )

    except BaseException:
        try:
            db.close()
        except UnboundLocalError:
            pass
        raise

    finally:
        os.umask(old_umask)

    return db


def get_locked(db, node):
    row = db.execute(
        "SELECT epoch,fingerprint,public_der,state "
        "FROM nodes WHERE node_id=?",
        (check_node(node),),
    ).fetchone()

    if row is None:
        raise IdentityError(
            "unknown node; explicit enrollment required"
        )

    epoch, fp, der, state = row

    der = bytes(der)

    if (
        fp != fingerprint(der)
        or state not in ("active", "revoked")
    ):
        raise IdentityError(
            "registry integrity check failed"
        )

    return epoch, fp, der, state


def enroll(path, node, public, expected_fp):
    der = key_der(public)
    fp = fingerprint(der)

    if (
        not isinstance(expected_fp, str)
        or fp != expected_fp
    ):
        raise IdentityError(
            "enrollment fingerprint not confirmed"
        )

    with closing(
        database(path, create=True)
    ) as db:

        db.execute("BEGIN IMMEDIATE")

        try:
            db.execute(
                "INSERT INTO nodes VALUES (?,?,?,?,?)",
                (
                    check_node(node),
                    0,
                    fp,
                    der,
                    "active",
                ),
            )

            digest = hashlib.sha256(
                ack.canonical(
                    {
                        "enroll": node,
                        "fingerprint": fp,
                    }
                )
            ).hexdigest()

            db.execute(
                "INSERT INTO events VALUES (?,?,?,?)",
                (
                    node,
                    0,
                    digest,
                    "enroll",
                ),
            )

            db.commit()

        except BaseException:
            db.rollback()
            raise

    return fp


def rotation_body(node, epoch, previous, new_der):
    return {
        "protocol": PROTO,
        "kind": "rotate",
        "chain_id": ack.CHAIN,
        "genesis_hash": ack.GENESIS,
        "node_id": check_node(node),
        "epoch": epoch,
        "old_fingerprint": previous,
        "new_fingerprint": fingerprint(new_der),
        "new_public_der_b64": base64.b64encode(
            new_der
        ).decode("ascii"),
    }


def revoke_body(node, epoch, previous):
    return {
        "protocol": PROTO,
        "kind": "revoke",
        "chain_id": ack.CHAIN,
        "genesis_hash": ack.GENESIS,
        "node_id": check_node(node),
        "epoch": epoch,
        "old_fingerprint": previous,
    }


def rotation_request(
    path,
    node,
    new_public,
    old_private,
    new_private,
):
    with closing(database(path)) as db:
        epoch, prev, _, state = get_locked(
            db,
            node,
        )

        if state != "active":
            raise IdentityError("node revoked")

        der = key_der(new_public)

        if fingerprint(der) == prev:
            raise IdentityError(
                "rotation must change the key"
            )

        body = rotation_body(
            node,
            epoch + 1,
            prev,
            der,
        )

        return {
            **body,
            "old_signature_hex": sign(
                old_private,
                body,
            ),
            "new_signature_hex": sign(
                new_private,
                body,
            ),
        }


def revocation_request(
    path,
    node,
    current_private,
):
    with closing(database(path)) as db:
        epoch, prev, _, state = get_locked(
            db,
            node,
        )

        if state != "active":
            raise IdentityError(
                "node already revoked"
            )

        body = revoke_body(
            node,
            epoch + 1,
            prev,
        )

        return {
            **body,
            "signature_hex": sign(
                current_private,
                body,
            ),
        }


def load_event(path):
    path = ack.require_regular_key(path)
    raw = path.read_bytes()

    if len(raw) > MAX_EVENT:
        raise IdentityError(
            "oversized event"
        )

    event = ack.strict_loads(raw)

    if not isinstance(event, dict):
        raise IdentityError(
            "event must be an object"
        )

    return event


def write_event(path, event):
    path = Path(path)

    if path.exists() or path.is_symlink():
        raise IdentityError(
            "event destination exists; refusing overwrite"
        )

    fd = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )

    with os.fdopen(fd, "wb") as f:
        f.write(
            ack.canonical(event) + b"\n"
        )

    return path


def apply_event(
    path,
    event,
    node,
    confirmed_fp=None,
):
    node = check_node(node)

    if not isinstance(event, dict):
        raise IdentityError(
            "event must be a JSON object"
        )

    kind = event.get("kind")

    if kind == "rotate":
        expected = set(
            rotation_body(
                node,
                0,
                "0" * 64,
                ED25519_SPKI + b"\x00" * 32,
            )
        )

        expected |= {
            "old_signature_hex",
            "new_signature_hex",
        }

    elif kind == "revoke":
        expected = set(
            revoke_body(
                node,
                0,
                "0" * 64,
            )
        ) | {"signature_hex"}

    else:
        raise IdentityError(
            "invalid event kind"
        )

    if set(event) != expected:
        raise IdentityError(
            "unexpected or missing event fields"
        )

    with closing(database(path)) as db:
        db.execute("BEGIN IMMEDIATE")

        try:
            epoch, prev, old_der, state = get_locked(
                db,
                node,
            )

            if state != "active":
                raise IdentityError(
                    "node is revoked"
                )

            if kind == "rotate":
                b64 = event["new_public_der_b64"]

                if not isinstance(b64, str):
                    raise IdentityError(
                        "bad DER encoding"
                    )

                new_der = check_der(
                    base64.b64decode(
                        b64,
                        validate=True,
                    )
                )

                if (
                    base64.b64encode(
                        new_der
                    ).decode("ascii") != b64
                ):
                    raise IdentityError(
                        "noncanonical DER encoding"
                    )

                body = rotation_body(
                    node,
                    epoch + 1,
                    prev,
                    new_der,
                )

                fp = fingerprint(new_der)

                if (
                    not isinstance(confirmed_fp, str)
                    or confirmed_fp != fp
                ):
                    raise IdentityError(
                        "new fingerprint not explicitly confirmed"
                    )

                if fp == prev:
                    raise IdentityError(
                        "identical new key"
                    )

                actual = {
                    k: event[k]
                    for k in body
                }

                if (
                    ack.canonical(actual)
                    != ack.canonical(body)
                ):
                    raise IdentityError(
                        "rotation event context or epoch mismatch"
                    )

                if not verify(
                    old_der,
                    body,
                    event["old_signature_hex"],
                ):
                    raise IdentityError(
                        "old key signature invalid"
                    )

                if not verify(
                    new_der,
                    body,
                    event["new_signature_hex"],
                ):
                    raise IdentityError(
                        "new key signature invalid"
                    )

                next_der = new_der
                next_fp = fp
                next_state = "active"

            else:
                body = revoke_body(
                    node,
                    epoch + 1,
                    prev,
                )

                actual = {
                    k: event[k]
                    for k in body
                }

                if (
                    ack.canonical(actual)
                    != ack.canonical(body)
                ):
                    raise IdentityError(
                        "revocation context or epoch mismatch"
                    )

                if not verify(
                    old_der,
                    body,
                    event["signature_hex"],
                ):
                    raise IdentityError(
                        "revocation signature invalid"
                    )

                next_der = old_der
                next_fp = prev
                next_state = "revoked"

            changed = db.execute(
                "UPDATE nodes SET "
                "epoch=?,fingerprint=?,"
                "public_der=?,state=? "
                "WHERE node_id=? AND epoch=? "
                "AND fingerprint=? AND state='active'",
                (
                    epoch + 1,
                    next_fp,
                    next_der,
                    next_state,
                    node,
                    epoch,
                    prev,
                ),
            )

            if changed.rowcount != 1:
                raise IdentityError(
                    "concurrent registry update"
                )

            digest = hashlib.sha256(
                ack.canonical(event)
            ).hexdigest()

            db.execute(
                "INSERT INTO events VALUES (?,?,?,?)",
                (
                    node,
                    epoch + 1,
                    digest,
                    kind,
                ),
            )

            db.commit()

            return (
                epoch + 1,
                next_fp,
                next_state,
            )

        except BaseException:
            db.rollback()
            raise


def inspect(path, node):
    with closing(database(path)) as db:
        epoch, fp, _, state = get_locked(
            db,
            node,
        )

        count = db.execute(
            "SELECT count(*) FROM events "
            "WHERE node_id=?",
            (node,),
        ).fetchone()[0]

        if count != epoch + 1:
            raise IdentityError(
                "audit history count mismatch"
            )

        return {
            "node_id": node,
            "epoch": epoch,
            "fingerprint": fp,
            "state": state,
            "history_events": count,
            "research_only": True,
            "independent_devices": False,
        }


def flush_once(
    identity_db,
    node,
    sender_db,
    peer,
):
    """Hold registry lock during v0.3 ACK verification."""

    with closing(
        database(identity_db)
    ) as db:

        db.execute("BEGIN IMMEDIATE")

        try:
            _, _, der, state = get_locked(
                db,
                node,
            )

            if state != "active":
                raise IdentityError(
                    "revoked node cannot acknowledge"
                )

            with tempfile.TemporaryDirectory(
                prefix="auneya-v04-pinned-"
            ) as tmp:

                pem = Path(tmp) / "pinned.pem"

                pem.write_bytes(
                    key_pem(der)
                )

                result = ack.flush_once(
                    sender_db,
                    peer,
                    pem,
                    node,
                )

            db.commit()
            return result

        except BaseException:
            db.rollback()
            raise


def self_test():
    with tempfile.TemporaryDirectory(
        prefix="auneya-v04-test-"
    ) as td:

        d = Path(td)

        packet, witness_pub = (
            ack.make_fixture_packet(d)
        )

        old_priv = d / "old.key"
        old_pub = d / "old.pub"
        new_priv = d / "new.key"
        new_pub = d / "new.pub"
        attacker_priv = d / "bad.key"
        attacker_pub = d / "bad.pub"

        umask = os.umask(0o077)

        try:
            for priv, pub in (
                (old_priv, old_pub),
                (new_priv, new_pub),
                (attacker_priv, attacker_pub),
            ):
                ack.run_openssl(
                    "genpkey",
                    "-algorithm",
                    "ED25519",
                    "-out",
                    priv,
                )

                ack.run_openssl(
                    "pkey",
                    "-in",
                    priv,
                    "-pubout",
                    "-out",
                    pub,
                )

                priv.chmod(0o600)

        finally:
            os.umask(umask)

        registry = d / "identity.sqlite"
        node = ack.RECEIVER_ID

        old_fp = fingerprint(
            key_der(old_pub)
        )

        new_fp = fingerprint(
            key_der(new_pub)
        )

        try:
            enroll(
                registry,
                node,
                old_pub,
                new_fp,
            )

            raise AssertionError(
                "wrong initial fingerprint accepted"
            )

        except IdentityError:
            print(
                "PASS: wrong enrollment fingerprint denied"
            )

        assert enroll(
            registry,
            node,
            old_pub,
            old_fp,
        ) == old_fp

        assert inspect(
            registry,
            node,
        )["epoch"] == 0

        try:
            enroll(
                registry,
                node,
                attacker_pub,
                fingerprint(
                    key_der(attacker_pub)
                ),
            )

            raise AssertionError(
                "identity replacement accepted"
            )

        except sqlite3.IntegrityError:
            print(
                "PASS: duplicate enrollment denied"
            )

        assert inspect(
            registry,
            node,
        )["fingerprint"] == old_fp

        print(
            "PASS: initial pinning and private registry"
        )

        rot = rotation_request(
            registry,
            node,
            new_pub,
            old_priv,
            new_priv,
        )

        assert rot["epoch"] == 1

        forged = dict(rot)

        unsigned = {
            k: v
            for k, v in rot.items()
            if not k.endswith("_signature_hex")
        }

        forged["old_signature_hex"] = sign(
            attacker_priv,
            unsigned,
        )

        negative_cases = [
            (
                "forged old key",
                forged,
                new_fp,
            ),
            (
                "wrong operator fingerprint",
                rot,
                old_fp,
            ),
            (
                "missing operator fingerprint",
                rot,
                None,
            ),
            (
                "foreign chain",
                {
                    **rot,
                    "chain_id":
                    "auneya-research-foreign-v1",
                },
                new_fp,
            ),
            (
                "future epoch",
                {
                    **rot,
                    "epoch": 9,
                },
                new_fp,
            ),
            (
                "epoch boolean type confusion",
                {
                    **rot,
                    "epoch": True,
                },
                new_fp,
            ),
            (
                "tampered new signature",
                {
                    **rot,
                    "new_signature_hex": "ff" * 64,
                },
                new_fp,
            ),
            (
                "foreign identity",
                {
                    **rot,
                    "node_id": "node_other_receiver_001",
                },
                new_fp,
            ),
        ]

        for label, event, confirmation in negative_cases:
            try:
                apply_event(
                    registry,
                    event,
                    node,
                    confirmation,
                )

                raise AssertionError(
                    f"accepted {label}"
                )

            except IdentityError:
                print(
                    "PASS: reject",
                    label,
                )

            assert inspect(
                registry,
                node,
            )["epoch"] == 0

        inbox = d / "receiver.sqlite"
        outbox = d / "sender-1.sqlite"

        mid = ack.queue(
            outbox,
            packet,
        )

        process, peer = ack.start_server(
            d,
            witness_pub,
            old_priv,
        )

        try:
            assert flush_once(
                registry,
                node,
                outbox,
                peer,
            )["status"] == "acked"

            assert ack.db_count(
                outbox,
                "outbox",
                "WHERE state='acked'",
            ) == 1

            assert ack.db_count(
                inbox,
                "inbox",
            ) == 1

            print(
                "PASS: v0.3 delivery with persisted "
                "trusted node identity"
            )

            outbox2 = d / "sender-2.sqlite"

            assert ack.queue(
                outbox2,
                packet,
            ) == mid

            assert apply_event(
                registry,
                rot,
                node,
                new_fp,
            ) == (
                1,
                new_fp,
                "active",
            )

            assert inspect(
                registry,
                node,
            )["epoch"] == 1

            assert flush_once(
                registry,
                node,
                outbox2,
                peer,
            )["status"] == "pending"

            print(
                "PASS: old ACK key fails after rotation"
            )

        finally:
            ack.stop_receiver(process)

        for label, event in (
            ("replayed rotation", rot),
            (
                "rollback epoch",
                {
                    **rot,
                    "epoch": 0,
                },
            ),
        ):
            try:
                apply_event(
                    registry,
                    event,
                    node,
                    new_fp,
                )

                raise AssertionError(
                    "accepted " + label
                )

            except IdentityError:
                print(
                    "PASS: reject",
                    label,
                )

        process, peer = ack.start_server(
            d,
            witness_pub,
            new_priv,
        )

        try:
            assert flush_once(
                registry,
                node,
                outbox2,
                peer,
            )["status"] == "acked"

            assert ack.db_count(
                inbox,
                "inbox",
            ) == 1

            print(
                "PASS: new ACK key trusted; "
                "duplicate proof remains unique"
            )

        finally:
            ack.stop_receiver(process)

        rev = revocation_request(
            registry,
            node,
            new_priv,
        )

        bad_rev = {
            **rev,
            "signature_hex": "00" * 64,
        }

        try:
            apply_event(
                registry,
                bad_rev,
                node,
            )

            raise AssertionError(
                "forged revocation accepted"
            )

        except IdentityError:
            print(
                "PASS: forged revocation rejected"
            )

        assert apply_event(
            registry,
            rev,
            node,
        ) == (
            2,
            new_fp,
            "revoked",
        )

        assert inspect(
            registry,
            node,
        )["state"] == "revoked"

        outbox3 = d / "sender-3.sqlite"

        ack.queue(
            outbox3,
            packet,
        )

        try:
            flush_once(
                registry,
                node,
                outbox3,
                "http://127.0.0.1:1/receive",
            )

            raise AssertionError(
                "revoked node usable"
            )

        except IdentityError:
            print(
                "PASS: revoked identity fails closed"
            )

        assert ack.db_count(
            outbox3,
            "outbox",
            "WHERE state='pending'",
        ) == 1

        for label, event in (
            ("revoke replay", rev),
            ("rotation after revoke", rot),
        ):
            try:
                apply_event(
                    registry,
                    event,
                    node,
                    new_fp,
                )

                raise AssertionError(label)

            except IdentityError:
                print(
                    "PASS: reject",
                    label,
                )

        print(
            json.dumps(
                {
                    "status": "PASS",
                    "version": PROTO,
                    "final_epoch": 2,
                    "final_state": "revoked",
                    "inbox_unique": 1,
                    "independent_devices": False,
                    "mainnet": False,
                    "token": False,
                }
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    sub = parser.add_subparsers(
        dest="action",
        required=True,
    )

    a = sub.add_parser("enroll")

    for name in (
        "registry",
        "node-id",
        "public",
        "confirm-fingerprint",
    ):
        a.add_argument(
            "--" + name,
            required=True,
        )

    a = sub.add_parser("fingerprint")

    a.add_argument(
        "--public",
        required=True,
    )

    a = sub.add_parser("inspect")

    for name in (
        "registry",
        "node-id",
    ):
        a.add_argument(
            "--" + name,
            required=True,
        )

    a = sub.add_parser("prepare-rotation")

    for name in (
        "registry",
        "node-id",
        "new-public",
        "old-private",
        "new-private",
        "output",
    ):
        a.add_argument(
            "--" + name,
            required=True,
        )

    a = sub.add_parser("prepare-revocation")

    for name in (
        "registry",
        "node-id",
        "current-private",
        "output",
    ):
        a.add_argument(
            "--" + name,
            required=True,
        )

    a = sub.add_parser("apply-event")

    for name in (
        "registry",
        "node-id",
        "event",
    ):
        a.add_argument(
            "--" + name,
            required=True,
        )

    a.add_argument(
        "--confirm-new-fingerprint"
    )

    for action in (
        "flush-once",
        "worker",
    ):
        a = sub.add_parser(action)

        for name in (
            "registry",
            "node-id",
            "database",
            "peer",
        ):
            a.add_argument(
                "--" + name,
                required=True,
            )

        if action == "worker":
            a.add_argument(
                "--interval",
                type=float,
                default=2.0,
            )

    sub.add_parser("self-test")

    args = parser.parse_args()

    if args.action == "self-test":
        return self_test()

    if args.action == "enroll":
        result = {
            "enrolled_fingerprint": enroll(
                args.registry,
                args.node_id,
                args.public,
                args.confirm_fingerprint,
            )
        }

    elif args.action == "fingerprint":
        result = {
            "fingerprint": fingerprint(
                key_der(args.public)
            )
        }

    elif args.action == "inspect":
        result = inspect(
            args.registry,
            args.node_id,
        )

    elif args.action == "prepare-rotation":
        event = rotation_request(
            args.registry,
            args.node_id,
            args.new_public,
            args.old_private,
            args.new_private,
        )

        result = {
            "event_file": str(
                write_event(
                    args.output,
                    event,
                )
            )
        }

    elif args.action == "prepare-revocation":
        event = revocation_request(
            args.registry,
            args.node_id,
            args.current_private,
        )

        result = {
            "event_file": str(
                write_event(
                    args.output,
                    event,
                )
            )
        }

    elif args.action == "apply-event":
        epoch, fp, state = apply_event(
            args.registry,
            load_event(args.event),
            args.node_id,
            args.confirm_new_fingerprint,
        )

        result = {
            "epoch": epoch,
            "fingerprint": fp,
            "state": state,
        }

    elif args.action == "flush-once":
        result = flush_once(
            args.registry,
            args.node_id,
            args.database,
            args.peer,
        )

    else:
        if not 0.2 <= args.interval <= 300:
            parser.error(
                "interval must be 0.2..300"
            )

        while True:
            print(
                json.dumps(
                    flush_once(
                        args.registry,
                        args.node_id,
                        args.database,
                        args.peer,
                    )
                ),
                flush=True,
            )

            import time
            time.sleep(args.interval)

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
