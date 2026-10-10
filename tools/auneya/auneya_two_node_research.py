#!/usr/bin/env python3
"""AUNEYA two-process loopback research network."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from auneya_attestation_binding import signing_message
from auneya_witness_proof_integration import (
    payload_hash,
    verify_proof,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT / "fixtures/auneya/witness-proofs/"
    "valid-download-integrity-prooflet.json"
)

CHAIN = "auneya-research-alpha-v1"
WITNESS = "witness_android_termux_001"
MAX_BYTES = 131072


def no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def http_post(url, packet):
    raw = json.dumps(
        packet,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()

    req = Request(
        url,
        raw,
        {"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.loads(
                response.read(4096)
            )
    except HTTPError as exc:
        return exc.code, json.loads(exc.read(4096))


def run_openssl(*args):
    subprocess.run(
        ["openssl", *map(str, args)],
        check=True,
        capture_output=True,
        timeout=15,
    )


def reply(handler, code, status):
    raw = json.dumps({"status": status}).encode()
    handler.send_response(code)
    handler.send_header(
        "Content-Type", "application/json"
    )
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


class NodeHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):
        cfg = self.server.config

        expected = (
            "/submit"
            if cfg.role == "sender"
            else "/receive"
        )

        if self.path != expected:
            return reply(self, 404, "not_found")

        try:
            length = int(
                self.headers.get("Content-Length", "0")
            )

            if not 0 < length <= MAX_BYTES:
                return reply(
                    self, 413, "invalid_length"
                )

            raw = self.rfile.read(length)

            packet = json.loads(
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

            if not isinstance(packet, dict):
                return reply(
                    self, 400, "invalid_envelope"
                )

            if set(packet) != required:
                return reply(
                    self, 400, "invalid_envelope"
                )

            if packet["version"] != (
                "auneya-loopback-v0.1"
            ):
                return reply(
                    self, 400, "invalid_version"
                )

            if (
                packet["chain_id"] != cfg.chain
                or packet["genesis_hash"] != cfg.genesis
            ):
                return reply(
                    self, 400, "wrong_chain_or_genesis"
                )

            proof = packet["proof"]

            if not isinstance(proof, dict):
                return reply(
                    self, 400, "invalid_proof"
                )

            sig_hex = packet["signature_hex"]

            if (
                not isinstance(sig_hex, str)
                or len(sig_hex) != 128
            ):
                return reply(
                    self, 400, "invalid_signature"
                )

            sig = bytes.fromhex(sig_hex)

            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "signature.bin"
                path.write_bytes(sig)

                valid = verify_proof(
                    proof,
                    cfg.chain,
                    cfg.witness,
                    cfg.public,
                    path,
                )

            if not valid:
                return reply(
                    self,
                    400,
                    "signature_or_schema_failed",
                )

            event_id = hashlib.sha256(
                (
                    cfg.chain
                    + "\x00"
                    + cfg.genesis
                    + "\x00"
                    + cfg.witness
                    + "\x00"
                    + payload_hash(proof)
                ).encode()
            ).hexdigest()

            db = self.server.database

            existing = db.execute(
                "SELECT 1 FROM accepted WHERE id=?",
                (event_id,),
            ).fetchone()

            if existing:
                return reply(
                    self, 409, "replay_rejected"
                )

            if cfg.role == "sender":
                try:
                    code, response = http_post(
                        cfg.peer, packet
                    )
                except (
                    URLError,
                    TimeoutError,
                    OSError,
                    ValueError,
                ):
                    return reply(
                        self, 502, "peer_unavailable"
                    )

                if (
                    code != 200
                    or response.get("status") != "accepted"
                ):
                    return reply(
                        self, 502, "peer_rejected"
                    )

            try:
                with db:
                    db.execute(
                        "INSERT INTO accepted "
                        "(id,received_at) VALUES (?,?)",
                        (event_id, int(time.time())),
                    )
            except sqlite3.IntegrityError:
                return reply(
                    self, 409, "replay_rejected"
                )

            return reply(self, 200, "accepted")

        except (
            ValueError,
            KeyError,
            TypeError,
            UnicodeError,
            OSError,
        ):
            return reply(self, 400, "malformed")


def serve(cfg):
    Path(cfg.database).parent.mkdir(
        parents=True, exist_ok=True
    )

    db = sqlite3.connect(cfg.database)

    db.execute(
        "CREATE TABLE IF NOT EXISTS accepted "
        "(id TEXT PRIMARY KEY, "
        "received_at INTEGER NOT NULL)"
    )

    with HTTPServer(
        ("127.0.0.1", 0), NodeHandler
    ) as server:
        server.config = cfg
        server.database = db

        port_path = Path(cfg.port_file)
        port_path.write_text(
            str(server.server_address[1]),
            encoding="ascii",
        )

        try:
            server.serve_forever()
        finally:
            port_path.unlink(missing_ok=True)
            db.close()


def start_node(role, folder, public, genesis, peer=""):
    port_file = folder / f"{role}.port"
    db_file = folder / f"{role}.sqlite3"

    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "serve",
        "--role", role,
        "--port-file", str(port_file),
        "--database", str(db_file),
        "--public", str(public),
        "--chain", CHAIN,
        "--genesis", genesis,
        "--witness", WITNESS,
    ]

    if peer:
        command += ["--peer", peer]

    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    deadline = time.monotonic() + 12

    while time.monotonic() < deadline:
        if port_file.exists():
            port = int(port_file.read_text())
            return (
                process,
                f"http://127.0.0.1:{port}",
            )

        if process.poll() is not None:
            error = process.stderr.read().decode()
            raise RuntimeError(error[-500:])

        time.sleep(0.05)

    process.terminate()
    raise TimeoutError(f"{role} did not start")


def self_test():
    with tempfile.TemporaryDirectory(
        prefix="auneya-2node-"
    ) as tmp:
        folder = Path(tmp)

        private = folder / "private.pem"
        public = folder / "public.pem"

        run_openssl(
            "genpkey",
            "-algorithm", "ED25519",
            "-out", private,
        )

        run_openssl(
            "pkey",
            "-in", private,
            "-pubout",
            "-out", public,
        )

        proof = json.loads(
            FIXTURE.read_text(encoding="utf-8")
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
            proof["witness"]["witness_id"] == WITNESS
        )

        genesis = "sha256:" + hashlib.sha256(
            (
                CHAIN
                + "\x00"
                + "AUNEYA-LOCAL-RESEARCH-GENESIS-V0.1"
            ).encode()
        ).hexdigest()

        packet = {
            "version": "auneya-loopback-v0.1",
            "chain_id": CHAIN,
            "genesis_hash": genesis,
            "proof": proof,
            "signature_hex": "",
        }

        message = folder / "message.bin"
        signature = folder / "signature.bin"

        message.write_bytes(
            signing_message(
                CHAIN,
                WITNESS,
                payload_hash(proof),
            )
        )

        run_openssl(
            "pkeyutl",
            "-sign",
            "-inkey", private,
            "-rawin",
            "-in", message,
            "-out", signature,
        )

        packet["signature_hex"] = (
            signature.read_bytes().hex()
        )

        processes = []

        try:
            node_b, receiver = start_node(
                "receiver",
                folder,
                public,
                genesis,
            )

            processes.append(node_b)

            node_a, sender = start_node(
                "sender",
                folder,
                public,
                genesis,
                receiver + "/receive",
            )

            processes.append(node_a)

            results = {}

            def check(name, candidate, expected):
                code, result = http_post(
                    sender + "/submit",
                    candidate,
                )

                if code != expected:
                    raise AssertionError(
                        f"{name}: got {code}, "
                        f"expected {expected}: {result}"
                    )

                results[name] = {
                    "code": code,
                    "status": result["status"],
                }

            altered = copy.deepcopy(packet)
            altered["proof"]["evidence"][0][
                "evidence_hash"
            ] = "sha256:" + "0" * 64

            bad_chain = copy.deepcopy(packet)
            bad_chain["chain_id"] = (
                "auneya-research-else-v1"
            )

            bad_genesis = copy.deepcopy(packet)
            bad_genesis["genesis_hash"] = (
                "sha256:" + "f" * 64
            )

            bad_signature = copy.deepcopy(packet)
            bad_signature["signature_hex"] = (
                "ff" * 64
            )

            bad_schema = copy.deepcopy(packet)
            bad_schema["proof"][
                "forbidden_field"
            ] = True

            check(
                "modified_payload_rejected",
                altered,
                400,
            )

            check(
                "wrong_chain_rejected",
                bad_chain,
                400,
            )

            check(
                "wrong_genesis_rejected",
                bad_genesis,
                400,
            )

            check(
                "forged_signature_rejected",
                bad_signature,
                400,
            )

            check(
                "schema_violation_rejected",
                bad_schema,
                400,
            )

            check(
                "valid_two_node_delivery",
                packet,
                200,
            )

            check(
                "replay_rejected",
                packet,
                409,
            )

            code, response = http_post(
                receiver + "/receive",
                packet,
            )

            assert code == 409, (code, response)

            results["receiver_persisted_replay"] = {
                "code": code,
                "status": response["status"],
            }

            for role in ("sender", "receiver"):
                with sqlite3.connect(
                    folder / f"{role}.sqlite3"
                ) as db:
                    count = db.execute(
                        "SELECT count(*) FROM accepted"
                    ).fetchone()[0]

                    assert count == 1, (
                        role, count
                    )

                results[role + "_db_count"] = count

            report = {
                "version": (
                    "auneya-two-node-loopback-v0.1"
                ),
                "status": "PASS",
                "checks": results,
                "chain_id": CHAIN,
                "genesis_hash": genesis,
                "independent_devices": False,
                "network_exposure": (
                    "127.0.0.1 only"
                ),
                "token_created": False,
                "mainnet": False,
            }

            out = (
                ROOT
                / ".tmp/auneya-two-node-loopback-v0.1"
            )

            out.mkdir(
                parents=True,
                exist_ok=True,
            )

            (out / "self-test.json").write_text(
                json.dumps(report, indent=2) + "\n",
                encoding="utf-8",
            )

            print(json.dumps(report, indent=2))

        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    process.terminate()

                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=3)

                if process.stderr:
                    process.stderr.close()


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    sub.add_parser("self-test")

    server = sub.add_parser("serve")

    server.add_argument(
        "--role",
        required=True,
        choices=["sender", "receiver"],
    )
    server.add_argument("--port-file", required=True)
    server.add_argument("--database", required=True)
    server.add_argument("--public", required=True)
    server.add_argument("--chain", required=True)
    server.add_argument("--genesis", required=True)
    server.add_argument("--witness", required=True)
    server.add_argument("--peer", default="")

    args = parser.parse_args()

    if args.command == "serve":
        serve(args)
    else:
        self_test()


if __name__ == "__main__":
    main()
