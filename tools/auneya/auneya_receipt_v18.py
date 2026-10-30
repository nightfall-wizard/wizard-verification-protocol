#!/usr/bin/env python3

"""
AUNEYA/WVP v1.8.

Authenticated local research receipts.

Extends existing:
- v1.6 signed peer evidence
- v1.7 bounded loopback transport
- existing persistent replay admission

No public P2P.
No network consensus.
No financial transactions.
No mainnet.
No token activation.
No independent audit.
"""

import argparse
import base64
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import time

import auneya_peer_gate_v16 as gate
import auneya_transport_v17 as net


FORMAT = 'auneya-signed-receipt-v1.8'

NONCE_SIZE = 32

MAX_RESPONSE = 2048

CRYPTO = Path(__file__).with_name(
    'auneya_receipt_crypto_v18.js'
)

FIELDS = {
    'format',
    'chain_id',
    'sender',
    'status',
    'frame_sha256',
    'nonce_b64',
    'responder_key_sha256',
    'local_replay_persisted',
    'non_value_research_only'
}


class ReceiptError(ValueError):
    pass


def need(condition, message):

    if not condition:
        raise ReceiptError(message)


def crypto(operation, key, payload, signature=None):

    request = {
        'op': operation,

        'key_b64': base64.b64encode(
            key
        ).decode('ascii'),

        'payload_b64': base64.b64encode(
            payload
        ).decode('ascii')
    }

    if signature is not None:
        request['signature_b64'] = signature

    try:

        result = subprocess.run(
            [
                'node',
                str(CRYPTO)
            ],
            input=gate.canonical(request),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=4,
            check=False
        )

    except (
        OSError,
        subprocess.TimeoutExpired
    ) as exc:

        raise ReceiptError(
            'receipt cryptography unavailable'
        ) from exc

    need(
        result.returncode == 0,
        'invalid receipt signature or key'
    )

    return result.stdout.decode('ascii')


def checked_public(path, expected_sha256):

    need(
        type(expected_sha256) is str
        and gate.HEX.fullmatch(
            expected_sha256
        ) is not None,
        'independent responder pin required'
    )

    public_key = gate.read_private(
        path,
        16384
    )

    need(
        gate.sha(public_key) == expected_sha256,
        'responder public-key pin mismatch'
    )

    return public_key


def signed_receipt(receipt, private_key):

    need(
        type(receipt) is dict
        and set(receipt) == FIELDS,
        'invalid receipt shape'
    )

    payload = gate.canonical(receipt)

    signature = crypto(
        'sign',
        private_key,
        payload
    )

    gate.b64decode(signature)

    return gate.canonical({
        'receipt': receipt,
        'signature_b64': signature
    }) + b'\n'


def verify_receipt(
    raw,
    public_key,
    expected_pin,
    nonce,
    original_frame
):

    need(
        len(raw) <= MAX_RESPONSE
        and raw.endswith(b'\n')
        and raw.count(b'\n') == 1,
        'invalid response framing'
    )

    obj = gate.strict_json(
        raw[:-1]
    )

    need(
        type(obj) is dict
        and set(obj) == {
            'receipt',
            'signature_b64'
        }
        and gate.canonical(obj) == raw[:-1],
        'noncanonical receipt response'
    )

    receipt = obj['receipt']

    need(
        type(receipt) is dict
        and set(receipt) == FIELDS,
        'invalid receipt fields'
    )

    need(
        type(receipt['status']) is str
        and receipt['status'] in (
            'ACCEPTED',
            'REJECTED'
        ),
        'invalid receipt status'
    )

    need(
        type(
            receipt['local_replay_persisted']
        ) is bool,
        'invalid persistence claim'
    )

    need(
        receipt['local_replay_persisted']
        == (
            receipt['status'] == 'ACCEPTED'
        ),
        'inconsistent receipt status'
    )

    need(
        receipt['non_value_research_only'] is True,
        'research boundary violation'
    )

    original = gate.decode_frame(
        original_frame
    )

    need(
        receipt['format'] == FORMAT
        and receipt['nonce_b64']
        == base64.b64encode(
            nonce
        ).decode('ascii')
        and receipt['frame_sha256']
        == gate.sha(original_frame)
        and receipt['responder_key_sha256']
        == expected_pin
        and receipt['chain_id']
        == original['chain_id']
        and receipt['sender']
        == original['sender'],
        'receipt/request binding mismatch'
    )

    gate.b64decode(
        obj['signature_b64']
    )

    result = crypto(
        'verify',
        public_key,
        gate.canonical(receipt),
        obj['signature_b64']
    )

    need(
        result == 'VERIFIED',
        'receipt signature verification failed'
    )

    return {
        'status': receipt['status'],
        'authenticated_ack': True,
        'frame_sha256':
            receipt['frame_sha256'],
        'local_replay_persisted':
            receipt['local_replay_persisted'],
        'non_value_research_only': True,
        'network_consensus_proven': False
    }


def accept_existing_gate(
    frame,
    policy,
    ledger
):

    trust = net.load_policy(policy)

    need(
        trust['enabled'],
        'revoked peer identity'
    )

    temporary = net.write_frame_tmp(
        Path(policy).absolute().parent,
        frame
    )

    try:

        gate.handle(
            'accept',
            temporary,
            trust['key_path'],
            trust['key_sha256'],
            trust['sender'],
            trust['chain_id'],
            trust['checkpoint_sha256'],
            trust['challenge_sha256'],
            trust['manifest_sha256'],
            ledger=ledger
        )

    finally:

        temporary.unlink(
            missing_ok=True
        )

    return trust


def connection(
    conn,
    policy,
    ledger,
    private_key,
    responder_pin
):

    deadline = (
        time.monotonic() +
        net.RECV_DEADLINE
    )

    nonce = net.recv_exact(
        conn,
        NONCE_SIZE,
        deadline
    )

    prefix = net.recv_exact(
        conn,
        4,
        deadline
    )

    length, = struct.unpack(
        '>I',
        prefix
    )

    need(
        0 < length <= gate.MAX_BODY,
        'frame size budget exceeded'
    )

    body = net.recv_exact(
        conn,
        length,
        deadline
    )

    remaining = (
        deadline -
        time.monotonic()
    )

    need(
        remaining > 0,
        'request deadline exceeded'
    )

    conn.settimeout(
        remaining
    )

    need(
        conn.recv(1) == b'',
        'trailing data or unclosed request'
    )

    frame = prefix + body

    parsed = gate.decode_frame(
        frame
    )

    status = 'REJECTED'

    try:

        accept_existing_gate(
            frame,
            policy,
            ledger
        )

        status = 'ACCEPTED'

    except (
        ValueError,
        OSError,
        TimeoutError,
        gate.sqlite3.DatabaseError
    ):

        pass

    receipt = {
        'format': FORMAT,

        'chain_id':
            parsed['chain_id'],

        'sender':
            parsed['sender'],

        'status':
            status,

        'frame_sha256':
            gate.sha(frame),

        'nonce_b64':
            base64.b64encode(
                nonce
            ).decode('ascii'),

        'responder_key_sha256':
            responder_pin,

        'local_replay_persisted':
            status == 'ACCEPTED',

        'non_value_research_only':
            True
    }

    return signed_receipt(
        receipt,
        private_key
    )


def serve(
    policy,
    ledger,
    ready_file,
    port,
    max_connections,
    idle_timeout,
    private_path,
    public_path,
    responder_pin
):

    need(
        0 <= port <= 65535,
        'invalid port'
    )

    need(
        1 <= max_connections <= net.MAX_ATTEMPTS,
        'connection limit exceeded'
    )

    need(
        1 <= idle_timeout <= 30,
        'invalid idle timeout'
    )

    net.load_policy(
        policy
    )

    net.safe_parent(
        ledger
    )

    ready_file = net.safe_parent(
        ready_file
    )

    need(
        not ready_file.exists()
        and not ready_file.is_symlink(),
        'ready file already exists'
    )

    public_key = checked_public(
        public_path,
        responder_pin
    )

    private_key = gate.read_private(
        private_path,
        16384
    )

    probe = gate.canonical({
        'format': FORMAT,
        'selftest': True
    })

    signature = crypto(
        'sign',
        private_key,
        probe
    )

    need(
        crypto(
            'verify',
            public_key,
            probe,
            signature
        ) == 'VERIFIED',
        'server signing key mismatch'
    )

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server:

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind(
            (
                net.HOST,
                port
            )
        )

        server.listen(8)

        server.settimeout(
            idle_timeout
        )

        actual_port = (
            server.getsockname()[1]
        )

        fd = os.open(
            ready_file,
            os.O_CREAT |
            os.O_EXCL |
            os.O_WRONLY |
            getattr(
                os,
                'O_NOFOLLOW',
                0
            ),
            0o600
        )

        with os.fdopen(
            fd,
            'wb'
        ) as f:

            f.write(
                gate.canonical({
                    'format': FORMAT,
                    'host': net.HOST,
                    'port': actual_port
                })
            )

            f.flush()

            os.fsync(
                f.fileno()
            )

        try:

            for _ in range(
                max_connections
            ):

                try:

                    conn, _address = (
                        server.accept()
                    )

                except socket.timeout:
                    break

                with conn:

                    try:

                        response = connection(
                            conn,
                            policy,
                            ledger,
                            private_key,
                            responder_pin
                        )

                    except (
                        ValueError,
                        OSError,
                        TimeoutError,
                        gate.sqlite3.DatabaseError
                    ):

                        response = (
                            b'{"status":"REJECTED"}\n'
                        )

                    try:

                        conn.settimeout(4)

                        conn.sendall(
                            response
                        )

                    except OSError:
                        pass

        finally:

            ready_file.unlink(
                missing_ok=True
            )


def send(
    frame_path,
    host,
    port,
    public_path,
    responder_pin
):

    net.validate_host(
        host
    )

    need(
        1 <= port <= 65535,
        'invalid destination port'
    )

    frame = gate.read_private(
        frame_path,
        gate.MAX_BODY + 4
    )

    gate.decode_frame(
        frame
    )

    public_key = checked_public(
        public_path,
        responder_pin
    )

    nonce = os.urandom(
        NONCE_SIZE
    )

    with socket.create_connection(
        (
            host,
            port
        ),
        timeout=4
    ) as conn:

        conn.settimeout(6)

        conn.sendall(
            nonce + frame
        )

        conn.shutdown(
            socket.SHUT_WR
        )

        response = bytearray()

        while len(response) <= MAX_RESPONSE:

            part = conn.recv(
                MAX_RESPONSE + 1 -
                len(response)
            )

            if not part:
                break

            response.extend(
                part
            )

        need(
            len(response) <= MAX_RESPONSE,
            'oversized response'
        )

    return verify_receipt(
        bytes(response),
        public_key,
        responder_pin,
        nonce,
        frame
    )


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    sub = parser.add_subparsers(
        dest='action',
        required=True
    )

    server = sub.add_parser(
        'serve'
    )

    for field in (
        'policy',
        'ledger',
        'ready-file',
        'server-private',
        'server-public',
        'server-pin'
    ):

        server.add_argument(
            '--' + field,
            required=True
        )

    server.add_argument(
        '--port',
        type=int,
        default=0
    )

    server.add_argument(
        '--max-connections',
        type=int,
        default=16
    )

    server.add_argument(
        '--idle-timeout',
        type=int,
        default=10
    )

    client = sub.add_parser(
        'send'
    )

    for field in (
        'frame',
        'server-public',
        'server-pin'
    ):

        client.add_argument(
            '--' + field,
            required=True
        )

    client.add_argument(
        '--host',
        default=net.HOST
    )

    client.add_argument(
        '--port',
        type=int,
        required=True
    )

    args = parser.parse_args()

    try:

        if args.action == 'serve':

            serve(
                args.policy,
                args.ledger,
                args.ready_file,
                args.port,
                args.max_connections,
                args.idle_timeout,
                args.server_private,
                args.server_public,
                args.server_pin
            )

        else:

            result = send(
                args.frame,
                args.host,
                args.port,
                args.server_public,
                args.server_pin
            )

            print(
                json.dumps(
                    result,
                    sort_keys=True
                )
            )

    except (
        ValueError,
        OSError,
        TimeoutError
    ) as exc:

        parser.exit(
            2,
            'FAIL-CLOSED: ' +
            str(exc) +
            '\n'
        )


if __name__ == '__main__':
    main()
