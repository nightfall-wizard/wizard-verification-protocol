#!/usr/bin/env python3
"""AUNEYA local reliable-delivery research v0.2."""

import argparse
import copy
from contextlib import closing
import hashlib
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from unittest.mock import patch

from auneya_attestation_binding import signing_message

from auneya_two_node_research import (
    CHAIN,
    FIXTURE,
    WITNESS,
    no_duplicate_keys,
    run_openssl,
)

from auneya_witness_proof_integration import (
    payload_hash,
    verify_proof,
)

VERSION = "auneya-durable-delivery-v0.2"

GENESIS = "sha256:" + hashlib.sha256(
    (
        CHAIN
        + "\x00"
        + "AUNEYA-LOCAL-RESEARCH-GENESIS-V0.1"
    ).encode()
).hexdigest()

MAX_BYTES = 131072

HEX128 = re.compile(r"^[a-f0-9]{128}$")


def canonical(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def message_id(packet):
    context = {
        "version": VERSION,
        "chain_id": packet["chain_id"],
        "genesis_hash": packet["genesis_hash"],
        "witness_id": packet["proof"]["witness"]["witness_id"],
        "proof_hash": payload_hash(packet["proof"]),
    }

    return hashlib.sha256(
        canonical(context)
    ).hexdigest()


def parse_packet(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError("oversize")

    obj = json.loads(
        raw,
        object_pairs_hook=no_duplicate_keys,
        parse_constant=lambda value: (
            _ for _ in ()
        ).throw(ValueError(value)),
    )

    required = {
        "version",
        "chain_id",
        "genesis_hash",
        "proof",
        "signature_hex",
    }

    if not isinstance(obj, dict):
        raise ValueError("invalid envelope")

    if set(obj) != required:
        raise ValueError("invalid fields")

    if obj["version"] != VERSION:
        raise ValueError("invalid version")

    if not isinstance(obj["proof"], dict):
        raise ValueError("invalid proof")

    if not isinstance(obj["chain_id"], str):
        raise ValueError("invalid chain")

    if not isinstance(obj["genesis_hash"], str):
        raise ValueError("invalid genesis")

    sig = obj["signature_hex"]

    if not isinstance(sig, str):
        raise ValueError("invalid signature")

    if not HEX128.fullmatch(sig):
        raise ValueError("invalid signature encoding")

    return obj


def connect(path, table):
    db_path = Path(path)

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    db = sqlite3.connect(
        db_path,
        timeout=5,
    )

    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA busy_timeout=5000")

    if table == "outbox":
        db.execute(
            "CREATE TABLE IF NOT EXISTS outbox ("
            "id TEXT PRIMARY KEY, "
            "packet TEXT NOT NULL, "
            "state TEXT NOT NULL "
            "CHECK(state IN ('pending','acked')), "
            "attempts INTEGER NOT NULL DEFAULT 0, "
            "last_error TEXT NOT NULL DEFAULT '')"
        )

    elif table == "inbox":
        db.execute(
            "CREATE TABLE IF NOT EXISTS inbox ("
            "id TEXT PRIMARY KEY, "
            "proof_hash TEXT NOT NULL, "
            "received_at INTEGER NOT NULL)"
        )

    else:
        raise ValueError("invalid database table")

    db.commit()

    return db


def queue(db_path, packet):
    raw = canonical(packet)

    parse_packet(raw)

    mid = message_id(packet)

    with closing(connect(db_path, "outbox")) as db:
        with db:
            db.execute(
                "INSERT OR IGNORE INTO outbox "
                "(id,packet,state) "
                "VALUES (?,?,'pending')",
                (
                    mid,
                    raw.decode("utf-8"),
                ),
            )

    return mid


def validate_peer(url):
    parsed = urlsplit(url)

    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or not parsed.port
        or parsed.path != "/receive"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "peer must use "
            "http://127.0.0.1:PORT/receive"
        )

    return url


def post(url, raw):
    validate_peer(url)

    req = Request(
        url,
        raw,
        {
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=3) as response:
            return (
                response.status,
                json.loads(response.read(4096)),
            )

    except HTTPError as exc:
        return (
            exc.code,
            json.loads(exc.read(4096)),
        )


def flush_once(db_path, peer):
    peer = validate_peer(peer)

    with closing(connect(db_path, "outbox")) as db:
        row = db.execute(
            "SELECT id, packet "
            "FROM outbox "
            "WHERE state='pending' "
            "ORDER BY rowid LIMIT 1"
        ).fetchone()

        if row is None:
            return {
                "status": "idle",
            }

        mid, packet = row

        try:
            code, result = post(
                peer,
                packet.encode("utf-8"),
            )

            good = (
                code == 200
                and isinstance(result, dict)
                and result.get("status")
                in (
                    "accepted",
                    "already_accepted",
                )
                and result.get("message_id") == mid
            )

            err = (
                ""
                if good
                else f"unacknowledged_{code}"
            )

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            ValueError,
            TypeError,
        ) as exc:
            good = False
            err = type(exc).__name__

        with db:
            db.execute(
                "UPDATE outbox "
                "SET state=?, "
                "attempts=attempts+1, "
                "last_error=? "
                "WHERE id=? AND state='pending'",
                (
                    "acked" if good else "pending",
                    err,
                    mid,
                ),
            )

        return {
            "status": (
                "acked" if good else "pending"
            ),
            "message_id": mid,
        }


def respond(handler, code, status, mid=None):
    out = {
        "status": status,
    }

    if mid is not None:
        out["message_id"] = mid

    raw = canonical(out)

    handler.send_response(code)

    handler.send_header(
        "Content-Type",
        "application/json",
    )

    handler.send_header(
        "Content-Length",
        str(len(raw)),
    )

    handler.end_headers()

    handler.wfile.write(raw)


class Receiver(BaseHTTPRequestHandler):

    def log_message(self, *args):
        pass

    def do_POST(self):
        if self.path != "/receive":
            return respond(
                self,
                404,
                "not_found",
            )

        cfg = self.server.config

        try:
            size = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

            if not 0 < size <= MAX_BYTES:
                return respond(
                    self,
                    413,
                    "invalid_length",
                )

            packet = parse_packet(
                self.rfile.read(size)
            )

            if (
                packet["chain_id"] != cfg.chain
                or packet["genesis_hash"]
                != cfg.genesis
            ):
                return respond(
                    self,
                    400,
                    "wrong_chain_or_genesis",
                )

            with tempfile.TemporaryDirectory() as tmp:
                signature = (
                    Path(tmp) / "signature.bin"
                )

                signature.write_bytes(
                    bytes.fromhex(
                        packet["signature_hex"]
                    )
                )

                valid = verify_proof(
                    packet["proof"],
                    cfg.chain,
                    cfg.witness,
                    cfg.public,
                    signature,
                )

                if not valid:
                    return respond(
                        self,
                        400,
                        "invalid_proof_or_signature",
                    )

            mid = message_id(packet)

            digest = payload_hash(
                packet["proof"]
            )

            db = self.server.db

            with db:
                cursor = db.execute(
                    "INSERT OR IGNORE INTO inbox "
                    "(id,proof_hash,received_at) "
                    "VALUES (?,?,?)",
                    (
                        mid,
                        digest,
                        int(time.time()),
                    ),
                )

            first = cursor.rowcount == 1

            if (
                first
                and cfg.drop_ack
                and not Path(cfg.drop_ack).exists()
            ):
                Path(cfg.drop_ack).write_text(
                    "ack intentionally lost\n"
                )

                return respond(
                    self,
                    503,
                    "test_ack_lost",
                )

            return respond(
                self,
                200,
                (
                    "accepted"
                    if first
                    else "already_accepted"
                ),
                mid,
            )

        except (
            OSError,
            KeyError,
            ValueError,
            TypeError,
            UnicodeError,
            sqlite3.Error,
        ):
            return respond(
                self,
                400,
                "malformed",
            )


def serve(args):
    if (
        args.chain != CHAIN
        or args.genesis != GENESIS
        or args.witness != WITNESS
    ):
        raise ValueError(
            "unexpected research identity"
        )

    pub = Path(args.public)

    if pub.is_symlink() or not pub.is_file():
        raise ValueError(
            "invalid trusted public key"
        )

    with closing(
        connect(args.database, "inbox")
    ) as db:

        with HTTPServer(
            ("127.0.0.1", args.port),
            Receiver,
        ) as server:

            server.db = db
            server.config = args

            port_path = Path(args.port_file)

            port_path.write_text(
                str(server.server_address[1])
            )

            try:
                server.serve_forever()

            finally:
                port_path.unlink(
                    missing_ok=True
                )


def make_fixture_packet(folder):
    private = folder / "private.pem"
    public = folder / "public.pem"

    run_openssl(
        "genpkey",
        "-algorithm",
        "ED25519",
        "-out",
        private,
    )

    run_openssl(
        "pkey",
        "-in",
        private,
        "-pubout",
        "-out",
        public,
    )

    proof = json.loads(
        FIXTURE.read_text(
            encoding="utf-8"
        )
    )

    proof["integrity"] = {
        "proof_hash": "",
        "signature_status": "signed",
        "signature_algorithm": "ed25519",
    }

    proof["integrity"]["proof_hash"] = (
        payload_hash(proof)
    )

    assert (
        proof["witness"]["witness_id"]
        == WITNESS
    )

    msg = folder / "msg.bin"
    sig = folder / "signature.bin"

    msg.write_bytes(
        signing_message(
            CHAIN,
            WITNESS,
            payload_hash(proof),
        )
    )

    run_openssl(
        "pkeyutl",
        "-sign",
        "-inkey",
        private,
        "-rawin",
        "-in",
        msg,
        "-out",
        sig,
    )

    packet = {
        "version": VERSION,
        "chain_id": CHAIN,
        "genesis_hash": GENESIS,
        "proof": proof,
        "signature_hex": (
            sig.read_bytes().hex()
        ),
    }

    return packet, public


def start_receiver(
    folder,
    public,
    drop_ack=None,
):
    port_file = folder / "port.txt"

    port_file.unlink(
        missing_ok=True
    )

    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "serve",
        "--database",
        str(folder / "receiver.sqlite"),
        "--public",
        str(public),
        "--port-file",
        str(port_file),
        "--chain",
        CHAIN,
        "--genesis",
        GENESIS,
        "--witness",
        WITNESS,
    ]

    if drop_ack:
        command += [
            "--drop-ack",
            str(drop_ack),
        ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    deadline = time.monotonic() + 10

    while time.monotonic() < deadline:
        if port_file.exists():
            port = int(
                port_file.read_text()
            )

            return (
                process,
                f"http://127.0.0.1:{port}/receive",
            )

        if process.poll() is not None:
            error = (
                process.stderr.read().decode()
            )

            raise RuntimeError(
                error[-1000:]
            )

        time.sleep(0.05)

    process.terminate()
    process.wait(timeout=3)

    raise TimeoutError(
        "receiver failed to start"
    )


def stop_receiver(process):
    if process.poll() is None:
        process.terminate()

        try:
            process.wait(
                timeout=3
            )

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

    process.stderr.close()


def db_count(
    path,
    table,
    where="",
):
    with closing(
        connect(path, table)
    ) as db:
        return db.execute(
            f"SELECT count(*) FROM {table} {where}"
        ).fetchone()[0]


def self_test():

    with tempfile.TemporaryDirectory(
        prefix="auneya-durable-v02-"
    ) as temp:

        folder = Path(temp)

        packet, public = (
            make_fixture_packet(folder)
        )

        outbox = folder / "sender.sqlite"

        mid = queue(
            outbox,
            packet,
        )

        assert queue(
            outbox,
            packet,
        ) == mid

        assert db_count(
            outbox,
            "outbox",
        ) == 1

        print(
            "PASS: persistent outbox created"
        )

        offline = flush_once(
            outbox,
            "http://127.0.0.1:1/receive",
        )

        assert (
            offline["status"]
            == "pending"
        )

        assert db_count(
            outbox,
            "outbox",
            "WHERE state='pending'",
        ) == 1

        print(
            "PASS: offline node preserves pending"
        )

        with patch(
            __name__ + ".post",
            return_value=(
                200,
                {
                    "status": "accepted",
                    "message_id": "0" * 64,
                },
            ),
        ):
            forged = flush_once(
                outbox,
                "http://127.0.0.1:1/receive",
            )

        assert (
            forged["status"]
            == "pending"
        )

        assert db_count(
            outbox,
            "outbox",
            "WHERE state='pending'",
        ) == 1

        print(
            "PASS: mismatched ACK rejected"
        )

        drop_ack = (
            folder / "lost-ack.marker"
        )

        process, peer = start_receiver(
            folder,
            public,
            drop_ack,
        )

        try:
            wrong_chain = copy.deepcopy(
                packet
            )

            wrong_chain["chain_id"] = (
                "auneya-research-foreign-v1"
            )

            assert post(
                peer,
                canonical(wrong_chain),
            )[0] == 400

            wrong_genesis = copy.deepcopy(
                packet
            )

            wrong_genesis["genesis_hash"] = (
                "sha256:" + "f" * 64
            )

            assert post(
                peer,
                canonical(wrong_genesis),
            )[0] == 400

            tampered = copy.deepcopy(
                packet
            )

            tampered["signature_hex"] = (
                "ff" * 64
            )

            assert post(
                peer,
                canonical(tampered),
            )[0] == 400

            bad_json = (
                b'{"version":1,"version":2}'
            )

            assert post(
                peer,
                bad_json,
            )[0] == 400

            assert db_count(
                folder / "receiver.sqlite",
                "inbox",
            ) == 0

            print(
                "PASS: invalid packets rejected"
            )

            first = flush_once(
                outbox,
                peer,
            )

            assert (
                first["status"]
                == "pending"
            ), first

            assert drop_ack.exists()

            assert db_count(
                folder / "receiver.sqlite",
                "inbox",
            ) == 1

            assert db_count(
                outbox,
                "outbox",
                "WHERE state='pending'",
            ) == 1

            print(
                "PASS: lost ACK after receiver commit"
            )

        finally:
            stop_receiver(process)

        process, peer = start_receiver(
            folder,
            public,
        )

        try:
            restarted = subprocess.run(
                [
                    sys.executable,
                    str(
                        Path(__file__).resolve()
                    ),
                    "flush-once",
                    "--database",
                    str(outbox),
                    "--peer",
                    peer,
                ],
                check=True,
                text=True,
                capture_output=True,
                timeout=12,
            )

            result = json.loads(
                restarted.stdout
            )

            assert (
                result["status"]
                == "acked"
            )

            assert db_count(
                outbox,
                "outbox",
                "WHERE state='acked'",
            ) == 1

            assert db_count(
                folder / "receiver.sqlite",
                "inbox",
            ) == 1

            print(
                "PASS: sender restart recovered"
            )

            print(
                "PASS: receiver restart recovered"
            )

            code, answer = post(
                peer,
                canonical(packet),
            )

            assert code == 200

            assert answer == {
                "status": "already_accepted",
                "message_id": mid,
            }

            assert db_count(
                folder / "receiver.sqlite",
                "inbox",
            ) == 1

            assert flush_once(
                outbox,
                peer,
            )["status"] == "idle"

            print(
                "PASS: exactly one inbox entry"
            )

            report = {
                "status": "PASS",
                "version": VERSION,
                "offline_preserved_pending": True,
                "forged_ack_rejected": True,
                "ack_lost_after_receiver_commit": True,
                "sender_restart_completed": True,
                "receiver_restart_completed": True,
                "outbox_acked": db_count(
                    outbox,
                    "outbox",
                    "WHERE state='acked'",
                ),
                "inbox_unique": db_count(
                    folder / "receiver.sqlite",
                    "inbox",
                ),
                "negative_cases": [
                    "chain",
                    "genesis",
                    "signature",
                    "duplicate_json_keys",
                ],
                "processes": "separate",
                "transport": "127.0.0.1 only",
                "independent_devices": False,
                "mainnet": False,
                "token": False,
            }

            print(
                json.dumps(
                    report,
                    indent=2,
                )
            )

        finally:
            stop_receiver(process)


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(
        dest="action",
        required=True,
    )

    server = sub.add_parser("serve")

    server.add_argument(
        "--database",
        required=True,
    )

    server.add_argument(
        "--port-file",
        required=True,
    )

    server.add_argument(
        "--public",
        required=True,
    )

    server.add_argument(
        "--port",
        type=int,
        default=0,
    )

    server.add_argument(
        "--chain",
        required=True,
    )

    server.add_argument(
        "--genesis",
        required=True,
    )

    server.add_argument(
        "--witness",
        required=True,
    )

    server.add_argument(
        "--drop-ack",
    )

    enqueue = sub.add_parser("queue")

    enqueue.add_argument(
        "--database",
        required=True,
    )

    enqueue.add_argument(
        "--packet",
        required=True,
    )

    one = sub.add_parser("flush-once")

    one.add_argument(
        "--database",
        required=True,
    )

    one.add_argument(
        "--peer",
        required=True,
    )

    worker = sub.add_parser("worker")

    worker.add_argument(
        "--database",
        required=True,
    )

    worker.add_argument(
        "--peer",
        required=True,
    )

    worker.add_argument(
        "--interval",
        type=float,
        default=2,
    )

    sub.add_parser("self-test")

    args = parser.parse_args()

    if args.action == "serve":
        serve(args)

    elif args.action == "queue":
        packet = parse_packet(
            Path(args.packet).read_bytes()
        )

        print(
            json.dumps(
                {
                    "queued_id": queue(
                        args.database,
                        packet,
                    )
                }
            )
        )

    elif args.action == "flush-once":
        print(
            json.dumps(
                flush_once(
                    args.database,
                    args.peer,
                )
            )
        )

    elif args.action == "worker":
        if not 0.2 <= args.interval <= 300:
            parser.error(
                "interval must be 0.2-300 seconds"
            )

        while True:
            print(
                json.dumps(
                    flush_once(
                        args.database,
                        args.peer,
                    )
                ),
                flush=True,
            )

            time.sleep(
                args.interval
            )

    else:
        self_test()


if __name__ == "__main__":
    main()
