#!/usr/bin/env python3

"""
AUNEYA v1.7

Authenticated bounded LOOPBACK-only
research transport.

Uses unchanged AUNEYA/WVP v1.6
Ed25519 peer envelope verification.

No public P2P network.
No trusted acknowledgment.
No independent audit.
No token.
No wallet.
No mainnet.
No consensus functionality.
"""

import argparse
import json
import os
from pathlib import Path
import socket
import struct
import sys
import tempfile
import time

import auneya_peer_gate_v16 as gate


POLICY_FORMAT = (
    'auneya-local-peer-policy-v1.7'
)

READY_FORMAT = (
    'auneya-loopback-ready-v1.7'
)

HOST = '127.0.0.1'

MAX_ATTEMPTS = 64

MAX_FRAME = gate.MAX_BODY + 4

MAX_POLICY = 8192

RECV_DEADLINE = 2.0

POLICY_FIELDS = {
    'format',
    'sender',
    'chain_id',
    'key_path',
    'key_sha256',
    'checkpoint_sha256',
    'challenge_sha256',
    'manifest_sha256',
    'enabled'
}


class TransportError(ValueError):
    pass


def require(condition, message):

    if not condition:
        raise TransportError(message)


def validate_host(host):

    require(
        host == HOST,
        'only 127.0.0.1 loopback is permitted'
    )


def safe_parent(path):

    path = Path(path).absolute()

    gate.private_dir(
        path.parent
    )

    return path


def atomic_policy(
    path,
    obj,
    replace=False
):

    p = safe_parent(path)

    raw = gate.canonical(obj)

    require(
        len(raw) <= MAX_POLICY,
        'policy size budget'
    )

    if not replace:

        fd = os.open(
            p,
            os.O_CREAT |
            os.O_EXCL |
            os.O_WRONLY |
            getattr(os, 'O_NOFOLLOW', 0),
            0o600
        )

        with os.fdopen(fd, 'wb') as f:

            f.write(raw)

            f.flush()

            os.fsync(
                f.fileno()
            )

    else:

        gate.read_private(
            p,
            MAX_POLICY
        )

        tmp = None

        try:

            with tempfile.NamedTemporaryFile(
                dir=p.parent,
                delete=False
            ) as f:

                tmp = Path(f.name)

                os.chmod(
                    tmp,
                    0o600
                )

                f.write(raw)

                f.flush()

                os.fsync(
                    f.fileno()
                )

            os.replace(
                tmp,
                p
            )

        finally:

            if tmp is not None:
                tmp.unlink(
                    missing_ok=True
                )

    fd = os.open(
        p.parent,
        os.O_RDONLY
    )

    try:

        os.fsync(fd)

    finally:

        os.close(fd)


def load_policy(
    path,
    verify_key=True
):

    raw = gate.read_private(
        path,
        MAX_POLICY
    )

    obj = gate.strict_json(raw)

    require(
        type(obj) is dict
        and set(obj) == POLICY_FIELDS,
        'invalid policy fields'
    )

    require(
        raw == gate.canonical(obj),
        'noncanonical policy'
    )

    require(
        obj['format'] == POLICY_FORMAT
        and type(obj['enabled']) is bool,
        'invalid policy format or status'
    )

    require(
        type(obj['sender']) is str
        and bool(
            gate.NAME.fullmatch(
                obj['sender']
            )
        ),
        'invalid sender'
    )

    require(
        type(obj['chain_id']) is str
        and bool(
            gate.CHAIN.fullmatch(
                obj['chain_id']
            )
        ),
        'invalid chain identity'
    )

    for field in (
        'key_sha256',
        'checkpoint_sha256',
        'challenge_sha256',
        'manifest_sha256'
    ):

        require(
            type(obj[field]) is str
            and bool(
                gate.HEX.fullmatch(
                    obj[field]
                )
            ),
            'invalid independent pin: ' + field
        )

    require(
        type(obj['key_path']) is str
        and Path(
            obj['key_path']
        ).is_absolute(),
        'key_path must be absolute'
    )

    if verify_key:

        require(
            gate.sha(
                gate.read_private(
                    obj['key_path'],
                    16384
                )
            ) == obj['key_sha256'],
            'enrolled public-key fingerprint mismatch'
        )

    return obj


def enroll(
    args,
    rotate=False
):

    p = safe_parent(
        args.policy
    )

    old = (
        load_policy(
            p,
            verify_key=False
        )
        if rotate
        else None
    )

    require(
        type(args.sender) is str
        and bool(
            gate.NAME.fullmatch(
                args.sender
            )
        ),
        'invalid sender'
    )

    require(
        type(args.chain_id) is str
        and bool(
            gate.CHAIN.fullmatch(
                args.chain_id
            )
        ),
        'invalid chain identity'
    )

    for value in (
        args.key_sha256,
        args.checkpoint_sha256,
        args.challenge_sha256,
        args.manifest_sha256
    ):

        require(
            bool(
                gate.HEX.fullmatch(
                    value
                )
            ),
            'invalid pinned SHA256'
        )

    key = Path(
        args.key
    ).absolute()

    require(
        gate.sha(
            gate.read_private(
                key,
                16384
            )
        ) == args.key_sha256,
        'key bytes differ from independently supplied fingerprint'
    )

    if rotate:

        require(
            old['enabled'],
            'cannot rotate revoked enrollment'
        )

        require(
            old['sender'] == args.sender
            and old['chain_id'] == args.chain_id,
            'rotation cannot change enrolled identity'
        )

        require(
            old['key_sha256'] != args.key_sha256,
            'rotation requires a different independently pinned key'
        )

    obj = {

        'format':
            POLICY_FORMAT,

        'sender':
            args.sender,

        'chain_id':
            args.chain_id,

        'key_path':
            str(key),

        'key_sha256':
            args.key_sha256,

        'checkpoint_sha256':
            args.checkpoint_sha256,

        'challenge_sha256':
            args.challenge_sha256,

        'manifest_sha256':
            args.manifest_sha256,

        'enabled':
            True
    }

    atomic_policy(
        p,
        obj,
        replace=rotate
    )

    print(
        json.dumps(
            {
                'status':
                    'ROTATED'
                    if rotate
                    else 'ENROLLED',

                'public_key_sha256':
                    args.key_sha256
            },
            sort_keys=True
        )
    )


def revoke(path):

    obj = load_policy(
        path,
        verify_key=False
    )

    require(
        obj['enabled'],
        'already revoked'
    )

    obj['enabled'] = False

    atomic_policy(
        path,
        obj,
        replace=True
    )

    print(
        '{"status":"REVOKED"}'
    )


def recv_exact(
    conn,
    count,
    deadline
):

    data = bytearray()

    while len(data) < count:

        remaining = (
            deadline -
            time.monotonic()
        )

        require(
            remaining > 0,
            'read deadline exceeded'
        )

        conn.settimeout(
            remaining
        )

        part = conn.recv(
            min(
                4096,
                count - len(data)
            )
        )

        require(
            bool(part),
            'truncated frame'
        )

        data.extend(part)

    return bytes(data)


def recv_frame(conn):

    deadline = (
        time.monotonic() +
        RECV_DEADLINE
    )

    prefix = recv_exact(
        conn,
        4,
        deadline
    )

    size, = struct.unpack(
        '>I',
        prefix
    )

    require(
        0 < size <= gate.MAX_BODY,
        'frame input budget exceeded'
    )

    body = recv_exact(
        conn,
        size,
        deadline
    )

    remain = (
        deadline -
        time.monotonic()
    )

    require(
        remain > 0,
        'read deadline exceeded'
    )

    conn.settimeout(
        remain
    )

    require(
        conn.recv(1) == b'',
        'trailing data or unclosed request'
    )

    return prefix + body


def write_frame_tmp(
    directory,
    frame
):

    with tempfile.NamedTemporaryFile(
        dir=directory,
        delete=False
    ) as f:

        name = Path(
            f.name
        )

        os.chmod(
            name,
            0o600
        )

        f.write(frame)

        f.flush()

    return name


def process_connection(
    conn,
    policy,
    ledger
):

    frame = recv_frame(
        conn
    )

    trust = load_policy(
        policy
    )

    require(
        trust['enabled'],
        'peer identity revoked'
    )

    temp = write_frame_tmp(
        Path(
            policy
        ).absolute().parent,
        frame
    )

    try:

        result = gate.handle(

            'accept',

            temp,

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

        temp.unlink(
            missing_ok=True
        )

    return {

        'status':
            'ACCEPTED',

        'frame_sha256':
            result['frame_sha256'],

        'local_replay_persisted':
            True,

        'authenticated_ack':
            False,

        'network_consensus_proven':
            False,

        'non_value_research_only':
            True
    }


def serve(
    policy,
    ledger,
    ready_file,
    port,
    max_connections,
    idle_timeout
):

    require(
        0 <= port <= 65535,
        'invalid port'
    )

    require(
        1 <= max_connections <= MAX_ATTEMPTS,
        'connection budget exceeded'
    )

    require(
        1 <= idle_timeout <= 30,
        'idle timeout budget exceeded'
    )

    load_policy(
        policy
    )

    safe_parent(
        ledger
    )

    ready = safe_parent(
        ready_file
    )

    require(
        not ready.exists()
        and not ready.is_symlink(),
        'ready file exists'
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
                HOST,
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
            ready,
            os.O_CREAT |
            os.O_EXCL |
            os.O_WRONLY,
            0o600
        )

        with os.fdopen(
            fd,
            'wb'
        ) as f:

            f.write(
                gate.canonical(
                    {
                        'format':
                            READY_FORMAT,

                        'host':
                            HOST,

                        'port':
                            actual_port
                    }
                )
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

                    conn, _addr = (
                        server.accept()
                    )

                except socket.timeout:
                    break

                with conn:

                    try:

                        response = process_connection(
                            conn,
                            policy,
                            ledger
                        )

                    except (
                        ValueError,
                        OSError,
                        TimeoutError,
                        gate.GateError,
                        gate.sqlite3.DatabaseError
                    ):

                        response = {
                            'status':
                                'REJECTED'
                        }

                    try:

                        conn.sendall(
                            gate.canonical(
                                response
                            ) + b'\n'
                        )

                    except OSError:
                        pass

        finally:

            ready.unlink(
                missing_ok=True
            )


def send_frame(
    frame,
    host,
    port
):

    validate_host(
        host
    )

    require(
        1 <= port <= 65535,
        'invalid destination port'
    )

    raw = gate.read_private(
        frame,
        MAX_FRAME
    )

    gate.decode_frame(
        raw
    )

    with socket.create_connection(
        (
            host,
            port
        ),
        timeout=3
    ) as conn:

        conn.settimeout(3)

        conn.sendall(
            raw
        )

        conn.shutdown(
            socket.SHUT_WR
        )

        chunks = bytearray()

        while len(chunks) <= 512:

            part = conn.recv(
                513 - len(chunks)
            )

            if not part:
                break

            chunks.extend(part)

        require(
            len(chunks) <= 512
            and chunks.endswith(b'\n'),
            'invalid server response'
        )

    obj = gate.strict_json(
        bytes(
            chunks[:-1]
        )
    )

    require(
        type(obj) is dict
        and obj.get(
            'status'
        ) in (
            'ACCEPTED',
            'REJECTED'
        ),
        'invalid server status'
    )

    return obj


def main():

    p = argparse.ArgumentParser(
        description=__doc__
    )

    sub = p.add_subparsers(
        dest='action',
        required=True
    )

    for action in (
        'enroll',
        'rotate'
    ):

        q = sub.add_parser(
            action
        )

        for name in (
            'policy',
            'key',
            'key-sha256',
            'sender',
            'chain-id',
            'checkpoint-sha256',
            'challenge-sha256',
            'manifest-sha256'
        ):

            q.add_argument(
                '--' + name,
                required=True
            )

    q = sub.add_parser(
        'revoke'
    )

    q.add_argument(
        '--policy',
        required=True
    )

    q = sub.add_parser(
        'serve'
    )

    for name in (
        'policy',
        'ledger',
        'ready-file'
    ):

        q.add_argument(
            '--' + name,
            required=True
        )

    q.add_argument(
        '--port',
        type=int,
        default=0
    )

    q.add_argument(
        '--max-connections',
        type=int,
        default=16
    )

    q.add_argument(
        '--idle-timeout',
        type=int,
        default=10
    )

    q = sub.add_parser(
        'send'
    )

    q.add_argument(
        '--frame',
        required=True
    )

    q.add_argument(
        '--host',
        default=HOST
    )

    q.add_argument(
        '--port',
        type=int,
        required=True
    )

    a = p.parse_args()

    try:

        if a.action == 'enroll':

            enroll(a)

        elif a.action == 'rotate':

            enroll(
                a,
                rotate=True
            )

        elif a.action == 'revoke':

            revoke(
                a.policy
            )

        elif a.action == 'serve':

            serve(
                a.policy,
                a.ledger,
                a.ready_file,
                a.port,
                a.max_connections,
                a.idle_timeout
            )

        else:

            print(
                json.dumps(
                    send_frame(
                        a.frame,
                        a.host,
                        a.port
                    ),
                    sort_keys=True
                )
            )

    except (
        ValueError,
        OSError,
        TimeoutError,
        gate.sqlite3.DatabaseError
    ) as exc:

        p.exit(
            2,
            'FAIL-CLOSED: ' +
            str(exc) +
            '\n'
        )


if __name__ == '__main__':
    main()
