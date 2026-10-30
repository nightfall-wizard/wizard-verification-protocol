#!/usr/bin/env python3

"""
AUNEYA/WVP v1.6

Bounded, pinned, authenticated offline peer
envelope gate.

Research mode only.

No networking, token, consensus or trusted time.
"""

import argparse
import base64
import hashlib
import json
import os

from pathlib import Path

import re
import sqlite3
import stat
import struct
import subprocess
import time


FORMAT = 'auneya-peer-envelope-v1.6'

MAX_BODY = 65536
MAX_DB_BYTES = 32 * 1024 * 1024
MAX_ROWS = 50000

MAX_WINDOW = 120
CLOCK_SKEW = 30

MAX_INT = 2**63 - 1

CRYPTO = Path(__file__).with_name(
    'auneya_peer_crypto_v16.js'
)

DOMAIN = b'AUNEYA/WVP:PEER:V1.6\0'

FIELDS = {
    'format',
    'chain_id',
    'sender',
    'epoch',
    'counter',
    'issued_at',
    'expires_at',
    'challenge_sha256',
    'manifest_sha256',
    'checkpoint_sha256',
    'public_key_sha256',
    'signature_b64'
}

HEX = re.compile(
    r'^[0-9a-f]{64}$'
)

NAME = re.compile(
    r'^[a-z0-9][a-z0-9._-]{0,63}$'
)

CHAIN = re.compile(
    r'^[a-z0-9][a-z0-9._-]{0,79}$'
)


class GateError(ValueError):
    pass


def need(ok, why):

    if not ok:
        raise GateError(why)


def sha(data):

    return hashlib.sha256(
        data
    ).hexdigest()


def canonical(obj):

    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=True,
        separators=(',', ':'),
        allow_nan=False
    ).encode('ascii')


def _pairs(items):

    result = {}

    for k, v in items:

        need(
            k not in result,
            'duplicate JSON key'
        )

        result[k] = v

    return result


def _reject_float(value):

    raise GateError(
        'non-integer JSON number'
    )


def strict_json(raw):

    try:

        return json.loads(
            raw.decode('utf-8'),
            object_pairs_hook=_pairs,
            parse_float=_reject_float,
            parse_constant=_reject_float
        )

    except (
        UnicodeError,
        json.JSONDecodeError,
        ValueError
    ) as exc:

        if isinstance(exc, GateError):
            raise

        raise GateError(
            'invalid JSON/UTF-8'
        ) from exc


def private_dir(path):

    p = Path(path)

    s = p.lstat()

    need(
        stat.S_ISDIR(s.st_mode)
        and not s.st_mode & 0o077,
        'private directory (0700) required'
    )

    return p


def read_private(path, maximum):

    path = Path(path).absolute()

    private_dir(
        path.parent
    )

    fd = os.open(
        path,
        os.O_RDONLY |
        getattr(os, 'O_NOFOLLOW', 0)
    )

    try:

        s = os.fstat(fd)

        need(
            stat.S_ISREG(s.st_mode)
            and s.st_nlink == 1
            and not s.st_mode & 0o077
            and 0 < s.st_size <= maximum,
            'private regular (0600) bounded input required'
        )

        with os.fdopen(
            os.dup(fd),
            'rb'
        ) as inp:

            raw = inp.read(
                maximum + 1
            )

        need(
            len(raw) == s.st_size,
            'input changed while reading'
        )

        return raw

    finally:

        os.close(fd)


def b64decode(value):

    need(
        isinstance(value, str),
        'signature type'
    )

    try:

        data = base64.b64decode(
            value,
            validate=True
        )

    except (
        ValueError,
        base64.binascii.Error
    ) as exc:

        raise GateError(
            'noncanonical base64'
        ) from exc

    need(
        base64.b64encode(
            data
        ).decode('ascii') == value
        and len(data) == 64,
        'invalid Ed25519 signature encoding'
    )

    return data


def decode_frame(raw):

    need(
        4 < len(raw) <= MAX_BODY + 4,
        'frame resource budget'
    )

    length, = struct.unpack(
        '>I',
        raw[:4]
    )

    need(
        0 < length <= MAX_BODY
        and length == len(raw) - 4,
        'frame length/trailing bytes mismatch'
    )

    body = raw[4:]

    obj = strict_json(body)

    need(
        type(obj) is dict
        and set(obj) == FIELDS,
        'envelope fields'
    )

    need(
        canonical(obj) == body,
        'noncanonical frame'
    )

    return obj


def inspect(
    frame,
    key,
    key_hash,
    sender,
    chain_id,
    pin,
    challenge,
    manifest,
    now=None
):

    now = (
        int(time.time())
        if now is None
        else now
    )

    need(
        type(now) is int
        and 0 <= now <= MAX_INT,
        'invalid local clock'
    )

    need(
        bool(NAME.fullmatch(sender))
        and bool(CHAIN.fullmatch(chain_id)),
        'invalid expected identity'
    )

    need(
        all(
            isinstance(v, str)
            and HEX.fullmatch(v)
            for v in (
                key_hash,
                pin,
                challenge,
                manifest
            )
        ),
        'independently supplied SHA256 pins required'
    )

    raw = read_private(
        frame,
        MAX_BODY + 4
    )

    obj = decode_frame(raw)

    need(
        obj['format'] == FORMAT
        and obj['sender'] == sender
        and obj['chain_id'] == chain_id,
        'peer or network identity mismatch'
    )

    need(
        all(
            type(obj[k]) is int
            and 1 <= obj[k] <= MAX_INT
            for k in (
                'epoch',
                'counter',
                'issued_at',
                'expires_at'
            )
        ),
        'invalid epoch/counter/timestamp'
    )

    issued = obj['issued_at']

    expires = obj['expires_at']

    need(
        1 <= expires - issued <= MAX_WINDOW
        and issued - CLOCK_SKEW <= now
        <= expires + CLOCK_SKEW,
        'message outside bounded local time window'
    )

    need(
        obj['public_key_sha256'] == key_hash
        and obj['checkpoint_sha256'] == pin
        and obj['challenge_sha256'] == challenge
        and obj['manifest_sha256'] == manifest,
        'independent anchor mismatch'
    )

    key_data = read_private(
        key,
        16384
    )

    need(
        sha(key_data) == key_hash,
        'public key pin mismatch'
    )

    b64decode(
        obj['signature_b64']
    )

    signed = {
        k: v
        for k, v in obj.items()
        if k != 'signature_b64'
    }

    payload = canonical(signed)

    request = canonical({

        'key_b64':
            base64.b64encode(
                key_data
            ).decode('ascii'),

        'payload_b64':
            base64.b64encode(
                payload
            ).decode('ascii'),

        'signature_b64':
            obj['signature_b64']

    })

    try:

        result = subprocess.run(
            [
                'node',
                str(CRYPTO)
            ],
            input=request,
            capture_output=True,
            timeout=20,
            check=False
        )

    except (
        OSError,
        subprocess.TimeoutExpired
    ) as exc:

        raise GateError(
            'independent Ed25519 verifier unavailable'
        ) from exc

    need(
        result.returncode == 0
        and result.stdout ==
        b'ED25519_VALID\n',
        'Ed25519 signature rejected'
    )

    return obj, sha(raw)


def safe_ledger(path):

    p = Path(path).absolute()

    private_dir(
        p.parent
    )

    try:

        fd = os.open(
            p,
            os.O_WRONLY |
            os.O_CREAT |
            os.O_EXCL |
            getattr(
                os,
                'O_NOFOLLOW',
                0
            ),
            0o600
        )

        os.close(fd)

    except FileExistsError:
        pass

    s = p.lstat()

    need(
        stat.S_ISREG(s.st_mode)
        and s.st_nlink == 1
        and not s.st_mode & 0o077
        and s.st_size <= MAX_DB_BYTES,
        'unsafe or oversized replay ledger'
    )

    return p


def commit(
    ledger,
    obj,
    now
):

    p = safe_ledger(
        ledger
    )

    db = sqlite3.connect(
        p,
        isolation_level=None,
        timeout=15
    )

    try:

        db.execute(
            'PRAGMA journal_mode=DELETE'
        )

        db.execute(
            'PRAGMA synchronous=FULL'
        )

        db.execute(
            'BEGIN IMMEDIATE'
        )

        try:

            db.execute(
                'CREATE TABLE IF NOT EXISTS peers ('
                'chain_id TEXT NOT NULL, '
                'sender TEXT NOT NULL, '
                'last_epoch INTEGER NOT NULL, '
                'last_counter INTEGER NOT NULL, '
                'last_now INTEGER NOT NULL, '
                'PRIMARY KEY(chain_id,sender))'
            )

            db.execute(
                'CREATE TABLE IF NOT EXISTS messages ('
                'chain_id TEXT NOT NULL, '
                'sender TEXT NOT NULL, '
                'epoch INTEGER NOT NULL, '
                'counter INTEGER NOT NULL, '
                'challenge_sha256 TEXT NOT NULL, '
                'manifest_sha256 TEXT NOT NULL, '
                'admitted_at INTEGER NOT NULL, '
                'PRIMARY KEY(chain_id,sender,epoch,counter), '
                'UNIQUE(chain_id,sender,challenge_sha256), '
                'UNIQUE(chain_id,sender,manifest_sha256))'
            )

            key = (
                obj['chain_id'],
                obj['sender']
            )

            row = db.execute(
                'SELECT '
                'last_epoch,last_counter,last_now '
                'FROM peers '
                'WHERE chain_id=? AND sender=?',
                key
            ).fetchone()

            epoch = obj['epoch']

            counter = obj['counter']

            if row is None:

                need(
                    epoch == 1
                    and counter == 1,
                    'first epoch/counter must be 1/1'
                )

            else:

                last_epoch, last_counter, last_now = row

                need(
                    now >= last_now,
                    'local clock rollback'
                )

                need(
                    (
                        epoch == last_epoch
                        and counter ==
                        last_counter + 1
                    )
                    or
                    (
                        epoch ==
                        last_epoch + 1
                        and counter == 1
                    ),
                    'REPLAY or noncontiguous peer counter/epoch'
                )

            count, = db.execute(
                'SELECT COUNT(*) FROM messages'
            ).fetchone()

            need(
                count < MAX_ROWS,
                'ledger capacity exhausted'
            )

            db.execute(
                'INSERT INTO messages '
                'VALUES (?,?,?,?,?,?,?)',
                (
                    *key,
                    epoch,
                    counter,
                    obj['challenge_sha256'],
                    obj['manifest_sha256'],
                    now
                )
            )

            db.execute(
                'INSERT INTO peers '
                'VALUES (?,?,?,?,?) '
                'ON CONFLICT(chain_id,sender) '
                'DO UPDATE SET '
                'last_epoch=excluded.last_epoch, '
                'last_counter=excluded.last_counter, '
                'last_now=excluded.last_now',
                (
                    *key,
                    epoch,
                    counter,
                    now
                )
            )

            db.commit()

        except Exception:

            db.rollback()

            raise

    except sqlite3.IntegrityError as exc:

        raise GateError(
            'REPLAY: duplicate evidence or ledger integrity'
        ) from exc

    finally:

        db.close()


def handle(
    action,
    frame,
    key,
    key_hash,
    sender,
    chain_id,
    pin,
    challenge,
    manifest,
    ledger=None,
    now=None
):

    obj, frame_hash = inspect(
        frame,
        key,
        key_hash,
        sender,
        chain_id,
        pin,
        challenge,
        manifest,
        now
    )

    current = (
        int(time.time())
        if now is None
        else now
    )

    if action == 'accept':

        need(
            ledger is not None,
            'ledger required for replay protection'
        )

        commit(
            ledger,
            obj,
            current
        )

    return {

        'format':
            FORMAT,

        'result':
            'SIGNED_PEER_ENVELOPE_ACCEPTED_ONCE'
            if action == 'accept'
            else
            'SIGNED_PEER_ENVELOPE_VERIFIED_ONLY',

        'frame_sha256':
            frame_hash,

        'sender':
            sender,

        'chain_id':
            chain_id,

        'epoch':
            obj['epoch'],

        'counter':
            obj['counter'],

        'authenticated_statement_only':
            True,

        'replay_persisted':
            action == 'accept',

        'independent_peer_proven':
            False,

        'trusted_time_proven':
            False,

        'network_transport_proven':
            False,

        'non_value_research_only':
            True
    }


def main():

    ap = argparse.ArgumentParser(
        description=__doc__
    )

    ap.add_argument(
        'action',
        choices=[
            'verify',
            'accept'
        ]
    )

    for name in (
        'frame',
        'key',
        'key-sha256',
        'sender',
        'chain-id',
        'checkpoint-sha256',
        'challenge-sha256',
        'manifest-sha256'
    ):

        ap.add_argument(
            '--' + name,
            required=True
        )

    ap.add_argument(
        '--ledger'
    )

    args = ap.parse_args()

    try:

        print(
            json.dumps(
                handle(
                    args.action,
                    args.frame,
                    args.key,
                    args.key_sha256,
                    args.sender,
                    args.chain_id,
                    args.checkpoint_sha256,
                    args.challenge_sha256,
                    args.manifest_sha256,
                    args.ledger
                ),
                sort_keys=True,
                indent=2
            )
        )

    except (
        GateError,
        OSError,
        sqlite3.DatabaseError,
        ValueError,
        KeyError,
        TypeError
    ) as exc:

        ap.exit(
            2,
            'FAIL-CLOSED: ' +
            str(exc) +
            '\n'
        )


if __name__ == '__main__':
    main()
