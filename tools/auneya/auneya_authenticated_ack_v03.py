#!/usr/bin/env python3
"""AUNEYA v0.3: signed ACKs for local research delivery."""

import argparse
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from unittest.mock import patch

from auneya_durable_delivery_v02 import (
    CHAIN,
    GENESIS,
    WITNESS,
    MAX_BYTES,
    canonical,
    connect,
    db_count,
    make_fixture_packet,
    message_id,
    no_duplicate_keys,
    parse_packet,
    queue,
    run_openssl,
    stop_receiver,
    validate_peer,
)

from auneya_witness_proof_integration import (
    payload_hash,
    verify_proof,
)

PROTOCOL = "auneya-authenticated-ack-v0.3"
DOMAIN = b"AUNEYA-RESEARCH-RECEIPT-V0.3\x00"
RECEIVER_ID = "node_receiver_research_001"

NODE_RE = re.compile(r"^node_[a-z0-9_]{8,80}$")
NONCE_RE = re.compile(r"^[0-9a-f]{32}$")
SIG_RE = re.compile(r"^[0-9a-f]{128}$")
MID_RE = re.compile(r"^[0-9a-f]{64}$")

ACK_FIELDS = {
    "protocol",
    "receiver_id",
    "chain_id",
    "genesis_hash",
    "message_id",
    "attempt_nonce",
    "status",
}


def strict_loads(data):
    if len(data) > MAX_BYTES:
        raise ValueError("oversized JSON")

    return json.loads(
        data,
        object_pairs_hook=no_duplicate_keys,
        parse_constant=lambda x: (
            _ for _ in ()
        ).throw(ValueError(x)),
    )


def require_regular_key(path):
    path = Path(path)

    if path.is_symlink() or not path.is_file():
        raise ValueError(
            "key must be regular file, not a symlink"
        )

    return path


def ack_payload(receiver_id, mid, nonce, status):
    if not NODE_RE.fullmatch(receiver_id):
        raise ValueError("bad receiver ID")

    if not MID_RE.fullmatch(mid):
        raise ValueError("bad message ID")

    if not NONCE_RE.fullmatch(nonce):
        raise ValueError("bad nonce")

    if status not in (
        "accepted",
        "already_accepted",
    ):
        raise ValueError("bad ACK state")

    return {
        "protocol": PROTOCOL,
        "receiver_id": receiver_id,
        "chain_id": CHAIN,
        "genesis_hash": GENESIS,
        "message_id": mid,
        "attempt_nonce": nonce,
        "status": status,
    }


def signature_message(body):
    if not isinstance(body, dict):
        raise ValueError("invalid ACK")

    if set(body) != ACK_FIELDS:
        raise ValueError("invalid ACK fields")

    return DOMAIN + canonical(body)


def sign_ack(
    private_key,
    receiver_id,
    mid,
    nonce,
    status,
):
    private_key = require_regular_key(private_key)

    body = ack_payload(
        receiver_id,
        mid,
        nonce,
        status,
    )

    with tempfile.TemporaryDirectory(
        prefix="auneya-ack-sign-"
    ) as tmp:

        msg = Path(tmp) / "msg"
        sig = Path(tmp) / "sig"

        msg.write_bytes(
            signature_message(body)
        )

        result = subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-sign",
                "-inkey",
                str(private_key),
                "-rawin",
                "-in",
                str(msg),
                "-out",
                str(sig),
            ],
            capture_output=True,
            timeout=15,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "ACK signing failed"
            )

        raw_sig = sig.read_bytes()

    if len(raw_sig) != 64:
        raise RuntimeError(
            "unexpected Ed25519 signature length"
        )

    return {
        **body,
        "signature_hex": raw_sig.hex(),
    }


def verify_ack(
    value,
    public_key,
    receiver_id,
    mid,
    nonce,
):
    try:
        public_key = require_regular_key(
            public_key
        )

        if not isinstance(value, dict):
            return False

        if set(value) != (
            ACK_FIELDS | {"signature_hex"}
        ):
            return False

        sig_hex = value["signature_hex"]

        if not isinstance(sig_hex, str):
            return False

        if not SIG_RE.fullmatch(sig_hex):
            return False

        wanted = ack_payload(
            receiver_id,
            mid,
            nonce,
            value["status"],
        )

        actual = {
            key: value[key]
            for key in ACK_FIELDS
        }

        if actual != wanted:
            return False

        with tempfile.TemporaryDirectory(
            prefix="auneya-ack-verify-"
        ) as tmp:

            msg = Path(tmp) / "msg"
            sig = Path(tmp) / "sig"

            msg.write_bytes(
                signature_message(wanted)
            )

            sig.write_bytes(
                bytes.fromhex(sig_hex)
            )

            result = subprocess.run(
                [
                    "openssl",
                    "pkeyutl",
                    "-verify",
                    "-pubin",
                    "-inkey",
                    str(public_key),
                    "-sigfile",
                    str(sig),
                    "-rawin",
                    "-in",
                    str(msg),
                ],
                capture_output=True,
                timeout=15,
            )

        return result.returncode == 0

    except (
        KeyError,
        ValueError,
        TypeError,
        OSError,
        subprocess.TimeoutExpired,
    ):
        return False


def request_post(peer, packet, nonce):
    validate_peer(peer)

    body = canonical(
        {
            "protocol": PROTOCOL,
            "attempt_nonce": nonce,
            "packet": packet,
        }
    )

    if len(body) > MAX_BYTES:
        raise ValueError(
            "oversized request"
        )

    req = Request(
        peer,
        body,
        {
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(
            req,
            timeout=3,
        ) as response:

            return (
                response.status,
                strict_loads(
                    response.read(4097)
                ),
            )

    except HTTPError as exc:
        return (
            exc.code,
            strict_loads(
                exc.read(4097)
            ),
        )


def flush_once(
    db_path,
    peer,
    public_key,
    receiver_id,
):
    validate_peer(peer)

    require_regular_key(public_key)

    if not NODE_RE.fullmatch(receiver_id):
        raise ValueError(
            "invalid pinned receiver ID"
        )

    with closing(
        connect(db_path, "outbox")
    ) as db:

        row = db.execute(
            "SELECT id,packet FROM outbox "
            "WHERE state='pending' "
            "ORDER BY rowid LIMIT 1"
        ).fetchone()

        if row is None:
            return {
                "status": "idle",
            }

        mid, packet_text = row

        nonce = secrets.token_hex(16)

        try:
            packet = parse_packet(
                packet_text.encode("utf-8")
            )

            if message_id(packet) != mid:
                raise ValueError(
                    "corrupt outbox packet"
                )

            if (
                packet["chain_id"] != CHAIN
                or packet["genesis_hash"] != GENESIS
            ):
                raise ValueError(
                    "invalid outbox context"
                )

            code, ack = request_post(
                peer,
                packet,
                nonce,
            )

            good = (
                code == 200
                and verify_ack(
                    ack,
                    public_key,
                    receiver_id,
                    mid,
                    nonce,
                )
            )

            error = (
                ""
                if good
                else f"ack_unverified_{code}"
            )

        except (
            ValueError,
            KeyError,
            TypeError,
            OSError,
            URLError,
            TimeoutError,
            sqlite3.Error,
            subprocess.TimeoutExpired,
        ) as exc:

            good = False
            error = type(exc).__name__

        with db:
            db.execute(
                "UPDATE outbox "
                "SET state=?, "
                "attempts=attempts+1, "
                "last_error=? "
                "WHERE id=? AND state='pending'",
                (
                    "acked" if good else "pending",
                    error,
                    mid,
                ),
            )

        return {
            "status": (
                "acked" if good else "pending"
            ),
            "message_id": mid,
        }


def respond(handler, code, value):
    raw = canonical(value)

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
                {"status": "not_found"},
            )

        cfg = self.server.config

        try:
            self.connection.settimeout(5)

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

            if not 0 < length <= MAX_BYTES:
                return respond(
                    self,
                    413,
                    {"status": "invalid_length"},
                )

            envelope = strict_loads(
                self.rfile.read(length)
            )

            required = {
                "protocol",
                "attempt_nonce",
                "packet",
            }

            if not isinstance(envelope, dict):
                raise ValueError(
                    "invalid envelope"
                )

            if set(envelope) != required:
                raise ValueError(
                    "invalid envelope fields"
                )

            nonce = envelope["attempt_nonce"]

            if envelope["protocol"] != PROTOCOL:
                raise ValueError(
                    "invalid protocol"
                )

            if not isinstance(nonce, str):
                raise ValueError(
                    "invalid nonce"
                )

            if not NONCE_RE.fullmatch(nonce):
                raise ValueError(
                    "invalid nonce encoding"
                )

            packet = parse_packet(
                canonical(envelope["packet"])
            )

            if (
                packet["chain_id"] != CHAIN
                or packet["genesis_hash"] != GENESIS
            ):
                return respond(
                    self,
                    400,
                    {
                        "status":
                        "wrong_chain_or_genesis"
                    },
                )

            with tempfile.TemporaryDirectory(
                prefix="auneya-proof-"
            ) as tmp:

                signature_file = (
                    Path(tmp) / "sig"
                )

                signature_file.write_bytes(
                    bytes.fromhex(
                        packet["signature_hex"]
                    )
                )

                valid = verify_proof(
                    packet["proof"],
                    CHAIN,
                    WITNESS,
                    cfg.witness_public,
                    signature_file,
                )

                if not valid:
                    return respond(
                        self,
                        400,
                        {
                            "status":
                            "invalid_proof_or_signature"
                        },
                    )

            mid = message_id(packet)

            with cfg.db:
                cursor = cfg.db.execute(
                    "INSERT OR IGNORE INTO inbox "
                    "(id,proof_hash,received_at) "
                    "VALUES (?,?,?)",
                    (
                        mid,
                        payload_hash(
                            packet["proof"]
                        ),
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
                    "simulated ACK loss\n"
                )

                return respond(
                    self,
                    503,
                    {"status": "test_ack_lost"},
                )

            ack = sign_ack(
                cfg.ack_private,
                cfg.receiver_id,
                mid,
                nonce,
                (
                    "accepted"
                    if first
                    else "already_accepted"
                ),
            )

            return respond(
                self,
                200,
                ack,
            )

        except (
            ValueError,
            TypeError,
            KeyError,
            OSError,
            sqlite3.Error,
            RuntimeError,
            subprocess.TimeoutExpired,
        ):
            return respond(
                self,
                400,
                {"status": "malformed"},
            )


def serve(args):
    if (
        args.chain,
        args.genesis,
        args.witness,
    ) != (
        CHAIN,
        GENESIS,
        WITNESS,
    ):
        raise ValueError(
            "unsupported research context"
        )

    if not NODE_RE.fullmatch(
        args.receiver_id
    ):
        raise ValueError(
            "invalid receiver ID"
        )

    require_regular_key(
        args.witness_public
    )

    private = require_regular_key(
        args.ack_private
    )

    if private.stat().st_mode & 0o077:
        raise ValueError(
            "ACK private key requires chmod 600"
        )

    with closing(
        connect(args.database, "inbox")
    ) as db:

        with HTTPServer(
            ("127.0.0.1", args.port),
            Receiver,
        ) as server:

            server.config = args
            server.config.db = db

            port_file = Path(
                args.port_file
            )

            port_file.write_text(
                str(server.server_address[1]),
                encoding="ascii",
            )

            try:
                server.serve_forever()

            finally:
                port_file.unlink(
                    missing_ok=True
                )


def start_server(
    folder,
    witness_pub,
    ack_priv,
    drop_ack=None,
):
    port_file = folder / "port.txt"

    port_file.unlink(
        missing_ok=True
    )

    argv = [
        sys.executable,
        str(Path(__file__).resolve()),
        "serve",
        "--database",
        str(folder / "receiver.sqlite"),
        "--port-file",
        str(port_file),
        "--witness-public",
        str(witness_pub),
        "--ack-private",
        str(ack_priv),
        "--receiver-id",
        RECEIVER_ID,
        "--chain",
        CHAIN,
        "--genesis",
        GENESIS,
        "--witness",
        WITNESS,
    ]

    if drop_ack:
        argv += [
            "--drop-ack",
            str(drop_ack),
        ]

    process = subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    deadline = time.monotonic() + 10

    while time.monotonic() < deadline:
        if port_file.exists():
            port = int(
                port_file.read_text(
                    encoding="ascii"
                )
            )

            return (
                process,
                f"http://127.0.0.1:{port}/receive",
            )

        if process.poll() is not None:
            raise RuntimeError(
                process.stderr.read().decode(
                    errors="replace"
                )[-1000:]
            )

        time.sleep(0.05)

    stop_receiver(process)

    raise TimeoutError(
        "receiver not ready"
    )


def expect(condition, label):
    if not condition:
        raise AssertionError(label)

    print("PASS:", label)


def self_test():
    with tempfile.TemporaryDirectory(
        prefix="auneya-ack-v03-"
    ) as temp:

        folder = Path(temp)

        packet, witness_pub = (
            make_fixture_packet(folder)
        )

        ack_priv = (
            folder / "receiver-ack-private.pem"
        )

        ack_pub = (
            folder / "receiver-ack-public.pem"
        )

        wrong_priv = (
            folder / "wrong-private.pem"
        )

        wrong_pub = (
            folder / "wrong-public.pem"
        )

        original_umask = os.umask(0o077)

        try:
            for priv, pub in (
                (ack_priv, ack_pub),
                (wrong_priv, wrong_pub),
            ):
                run_openssl(
                    "genpkey",
                    "-algorithm",
                    "ED25519",
                    "-out",
                    priv,
                )

                run_openssl(
                    "pkey",
                    "-in",
                    priv,
                    "-pubout",
                    "-out",
                    pub,
                )

                priv.chmod(0o600)

        finally:
            os.umask(original_umask)

        sender_db = (
            folder / "sender.sqlite"
        )

        mid = queue(
            sender_db,
            packet,
        )

        expect(
            queue(sender_db, packet) == mid
            and db_count(
                sender_db,
                "outbox",
            ) == 1,
            "outbox enqueues one unique message",
        )

        offline = flush_once(
            sender_db,
            "http://127.0.0.1:1/receive",
            ack_pub,
            RECEIVER_ID,
        )

        expect(
            offline["status"] == "pending",
            "offline ACK never confirms",
        )

        nonce1 = "a" * 32
        nonce2 = "b" * 32

        valid = sign_ack(
            ack_priv,
            RECEIVER_ID,
            mid,
            nonce1,
            "accepted",
        )

        expect(
            verify_ack(
                valid,
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
            "valid Ed25519 ACK",
        )

        negative_cases = [
            (
                "replayed nonce",
                valid,
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce2,
            ),
            (
                "wrong receiver ID",
                valid,
                ack_pub,
                "node_alternative_receiver",
                mid,
                nonce1,
            ),
            (
                "wrong message ID",
                valid,
                ack_pub,
                RECEIVER_ID,
                "0" * 64,
                nonce1,
            ),
            (
                "wrong public key",
                valid,
                wrong_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
            (
                "modified status",
                {
                    **valid,
                    "status": "already_accepted",
                },
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
            (
                "modified chain",
                {
                    **valid,
                    "chain_id":
                    "auneya-research-foreign-v1",
                },
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
            (
                "modified genesis",
                {
                    **valid,
                    "genesis_hash":
                    "sha256:" + "0" * 64,
                },
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
            (
                "forged signature",
                {
                    **valid,
                    "signature_hex": "ff" * 64,
                },
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
            (
                "unsigned ACK",
                {
                    k: v
                    for k, v in valid.items()
                    if k != "signature_hex"
                },
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
            (
                "extra ACK field",
                {
                    **valid,
                    "extra": True,
                },
                ack_pub,
                RECEIVER_ID,
                mid,
                nonce1,
            ),
        ]

        for (
            name,
            modified,
            public,
            node,
            message,
            nonce,
        ) in negative_cases:

            expect(
                not verify_ack(
                    modified,
                    public,
                    node,
                    message,
                    nonce,
                ),
                "reject " + name,
            )

        with patch(
            __name__ + ".request_post",
            return_value=(200, valid),
        ), patch(
            __name__ + ".secrets.token_hex",
            return_value=nonce2,
        ):

            forged = flush_once(
                sender_db,
                "http://127.0.0.1:1/receive",
                ack_pub,
                RECEIVER_ID,
            )

        expect(
            forged["status"] == "pending",
            "captured ACK replay does not advance outbox",
        )

        lost = folder / "lost-ack"

        process, peer = start_server(
            folder,
            witness_pub,
            ack_priv,
            lost,
        )

        try:
            wrong_chain = {
                **packet,
                "chain_id":
                "auneya-research-foreign-v1",
            }

            wrong_genesis = {
                **packet,
                "genesis_hash":
                "sha256:" + "f" * 64,
            }

            wrong_signature = {
                **packet,
                "signature_hex": "ff" * 64,
            }

            for name, candidate in (
                ("wrong chain", wrong_chain),
                ("wrong genesis", wrong_genesis),
                (
                    "forged proof signature",
                    wrong_signature,
                ),
            ):
                code, _ = request_post(
                    peer,
                    candidate,
                    secrets.token_hex(16),
                )

                expect(
                    code == 400,
                    "reject " + name,
                )

            raw = (
                b'{"protocol":'
                b'"auneya-authenticated-ack-v0.3",'
                b'"protocol":"duplicate"}'
            )

            try:
                req = Request(
                    peer,
                    raw,
                    {
                        "Content-Type":
                        "application/json"
                    },
                    method="POST",
                )

                urlopen(
                    req,
                    timeout=3,
                )

                raise AssertionError(
                    "duplicate JSON key accepted"
                )

            except HTTPError as exc:
                expect(
                    exc.code == 400,
                    "reject duplicate JSON keys",
                )

            expect(
                db_count(
                    folder / "receiver.sqlite",
                    "inbox",
                ) == 0,
                "invalid requests not persisted",
            )

            result = flush_once(
                sender_db,
                peer,
                ack_pub,
                RECEIVER_ID,
            )

            expect(
                result["status"] == "pending"
                and lost.exists(),
                "lost ACK leaves durable pending",
            )

            expect(
                db_count(
                    folder / "receiver.sqlite",
                    "inbox",
                ) == 1,
                "receiver commits before lost ACK",
            )

            wrong_key = flush_once(
                sender_db,
                peer,
                wrong_pub,
                RECEIVER_ID,
            )

            expect(
                wrong_key["status"] == "pending",
                "wrong pinned ACK key keeps pending",
            )

        finally:
            stop_receiver(process)

        process, peer = start_server(
            folder,
            witness_pub,
            ack_priv,
        )

        try:
            restarted = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "flush-once",
                    "--database",
                    str(sender_db),
                    "--peer",
                    peer,
                    "--ack-public",
                    str(ack_pub),
                    "--receiver-id",
                    RECEIVER_ID,
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=12,
            )

            expect(
                json.loads(
                    restarted.stdout
                )["status"] == "acked",
                "restart accepts signed duplicate ACK",
            )

            expect(
                db_count(
                    sender_db,
                    "outbox",
                    "WHERE state='acked'",
                ) == 1,
                "signed receipt persisted as acked",
            )

            expect(
                db_count(
                    folder / "receiver.sqlite",
                    "inbox",
                ) == 1,
                "receiver retains exactly one proof",
            )

            code, ack = request_post(
                peer,
                packet,
                nonce2,
            )

            expect(
                code == 200
                and ack.get("status")
                == "already_accepted"
                and verify_ack(
                    ack,
                    ack_pub,
                    RECEIVER_ID,
                    mid,
                    nonce2,
                ),
                "duplicate delivery returns fresh signed ACK",
            )

            expect(
                flush_once(
                    sender_db,
                    peer,
                    ack_pub,
                    RECEIVER_ID,
                )["status"] == "idle",
                "no repeat after confirmed delivery",
            )

        finally:
            stop_receiver(process)

        report = {
            "status": "PASS",
            "version": PROTOCOL,
            "outbox_acked": db_count(
                sender_db,
                "outbox",
                "WHERE state='acked'",
            ),
            "inbox_unique": db_count(
                folder / "receiver.sqlite",
                "inbox",
            ),
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


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(
        dest="action",
        required=True,
    )

    server = sub.add_parser("serve")

    for name in (
        "database",
        "port-file",
        "witness-public",
        "ack-private",
        "receiver-id",
        "chain",
        "genesis",
        "witness",
    ):
        server.add_argument(
            "--" + name,
            required=True,
        )

    server.add_argument(
        "--port",
        type=int,
        default=0,
    )

    server.add_argument(
        "--drop-ack",
    )

    one = sub.add_parser("flush-once")
    worker = sub.add_parser("worker")

    for target in (one, worker):
        for name in (
            "database",
            "peer",
            "ack-public",
            "receiver-id",
        ):
            target.add_argument(
                "--" + name,
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

    elif args.action == "flush-once":
        result = flush_once(
            args.database,
            args.peer,
            args.ack_public,
            args.receiver_id,
        )

        print(json.dumps(result))

    elif args.action == "worker":
        if not 0.2 <= args.interval <= 300:
            parser.error(
                "interval must be 0.2-300 seconds"
            )

        while True:
            result = flush_once(
                args.database,
                args.peer,
                args.ack_public,
                args.receiver_id,
            )

            print(
                json.dumps(result),
                flush=True,
            )

            time.sleep(args.interval)

    else:
        self_test()


if __name__ == "__main__":
    main()
