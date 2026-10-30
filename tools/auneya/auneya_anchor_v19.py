#!/usr/bin/env python3

"""
AUNEYA/WVP v1.9.

Privately signed, externally retainable
research replay snapshots.

Not an external service.
Not distributed consensus.
Not trusted time.
Not a production network.

The operator must retain the latest signed
anchor outside the storage rollback domain.
"""

import argparse
import base64
import json
import os

from pathlib import Path

import sqlite3
import stat
import subprocess

from urllib.parse import quote

import auneya_peer_gate_v16 as gate


FORMAT = (
    'auneya-external-replay-anchor-v1.9'
)

CRYPTO = Path(__file__).with_name(
    'auneya_anchor_crypto_v19.js'
)

MAX_ANCHOR = 1024 * 1024

ZERO = '0' * 64

BODY_FIELDS = {
    'format',
    'chain_id',
    'sequence',
    'previous_sha256',
    'public_key_sha256',
    'messages_sha256',
    'state_sha256',
    'message_count',
    'peer_count',
    'tips',
    'non_value_research_only'
}


class AnchorError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise AnchorError(message)


def private_file(path, limit):
    return gate.read_private(
        path,
        limit
    )


def check_pin(public, pin):
    need(
        type(pin) is str
        and gate.HEX.fullmatch(pin) is not None,
        'independent signer SHA256 pin required'
    )

    key = private_file(
        public,
        16384
    )

    need(
        gate.sha(key) == pin,
        'signer key pin mismatch'
    )

    return key


def crypto(op, key, payload, signature=None):
    req = {
        'op': op,

        'key_b64':
            base64.b64encode(
                key
            ).decode('ascii'),

        'payload_b64':
            base64.b64encode(
                payload
            ).decode('ascii')
    }

    if signature is not None:
        req['signature_b64'] = signature

    try:
        result = subprocess.run(
            [
                'node',
                str(CRYPTO)
            ],

            input=gate.canonical(req),
            capture_output=True,
            timeout=8,
            check=False
        )

    except (
        OSError,
        subprocess.TimeoutExpired
    ) as exc:

        raise AnchorError(
            'Ed25519 engine unavailable'
        ) from exc

    need(
        result.returncode == 0,
        'Ed25519 signature rejected'
    )

    return result.stdout.decode('ascii')


def ledger_state(path, chain):
    need(
        type(chain) is str
        and bool(
            gate.CHAIN.fullmatch(chain)
        ),
        'invalid research chain identity'
    )

    p = Path(path).absolute()

    gate.private_dir(
        p.parent
    )

    st = p.lstat()

    need(
        stat.S_ISREG(st.st_mode)
        and st.st_nlink == 1
        and not st.st_mode & 0o077
        and 0 < st.st_size <= gate.MAX_DB_BYTES,
        'private regular bounded v1.6 ledger required'
    )

    uri = (
        'file:' +
        quote(
            str(p),
            safe='/'
        ) +
        '?mode=ro'
    )

    db = sqlite3.connect(
        uri,
        uri=True,
        timeout=8,
        isolation_level=None
    )

    try:
        db.execute(
            'PRAGMA query_only=ON'
        )

        db.execute('BEGIN')

        need(
            db.execute(
                'PRAGMA quick_check'
            ).fetchone() == ('ok',),
            'SQLite integrity check failed'
        )

        peers = [
            list(r)

            for r in db.execute(
                'SELECT '
                'sender,last_epoch,last_counter,last_now '
                'FROM peers '
                'WHERE chain_id=? '
                'ORDER BY sender',

                (chain,)
            )
        ]

        msgs = [
            list(r)

            for r in db.execute(
                'SELECT '
                'sender,epoch,counter,'
                'challenge_sha256,manifest_sha256,'
                'admitted_at '
                'FROM messages '
                'WHERE chain_id=? '
                'ORDER BY sender,epoch,counter',

                (chain,)
            )
        ]

        db.execute('COMMIT')

    finally:
        db.close()

    st2 = p.lstat()

    need(
        (
            st.st_dev,
            st.st_ino
        ) == (
            st2.st_dev,
            st2.st_ino
        ),
        'ledger swapped during snapshot'
    )

    need(
        0 < len(msgs) <= gate.MAX_ROWS
        and len(peers) <= len(msgs),
        'empty/oversized research ledger'
    )

    prior = {}

    challenges = set()
    manifests = set()

    for (
        sender,
        epoch,
        counter,
        challenge,
        manifest,
        admitted
    ) in msgs:

        need(
            type(sender) is str
            and bool(
                gate.NAME.fullmatch(sender)
            ),
            'invalid sender'
        )

        need(
            all(
                type(v) is int
                and 1 <= v <= gate.MAX_INT

                for v in (
                    epoch,
                    counter,
                    admitted
                )
            ),
            'invalid replay numbers'
        )

        need(
            all(
                type(v) is str
                and gate.HEX.fullmatch(v) is not None

                for v in (
                    challenge,
                    manifest
                )
            ),
            'invalid evidence hash'
        )

        need(
            (sender, challenge) not in challenges
            and (sender, manifest) not in manifests,
            'duplicate replay evidence'
        )

        challenges.add(
            (sender, challenge)
        )

        manifests.add(
            (sender, manifest)
        )

        last = prior.get(sender)

        if last is None:
            need(
                epoch == 1
                and counter == 1,
                'missing initial sender sequence'
            )

        else:
            old_e, old_c, old_t = last

            need(
                admitted >= old_t,
                'local timestamp regression'
            )

            need(
                (
                    epoch == old_e
                    and counter == old_c + 1
                )
                or
                (
                    epoch == old_e + 1
                    and counter == 1
                ),
                'gap or rollback in replay history'
            )

        prior[sender] = (
            epoch,
            counter,
            admitted
        )

    need(
        len(peers) == len(prior),
        'peer/message table mismatch'
    )

    for (
        sender,
        epoch,
        counter,
        now
    ) in peers:

        need(
            type(sender) is str
            and sender in prior
            and (
                epoch,
                counter,
                now
            ) == prior[sender],
            'peer tip disagrees with durable messages'
        )

    return {
        'chain_id': chain,
        'tips': peers,
        'messages': msgs
    }


def message_hash(chain, rows):
    return gate.sha(
        gate.canonical({
            'chain_id': chain,
            'messages': rows
        })
    )


def state_hash(state):
    return gate.sha(
        gate.canonical(state)
    )


def load_anchor(path, public_key, pin):
    raw = private_file(
        path,
        MAX_ANCHOR
    )

    need(
        raw.endswith(b'\n')
        and raw.count(b'\n') == 1,
        'invalid anchor framing'
    )

    obj = gate.strict_json(
        raw[:-1]
    )

    need(
        type(obj) is dict
        and set(obj) == {
            'body',
            'signature_b64'
        }
        and gate.canonical(obj) + b'\n' == raw,
        'noncanonical anchor'
    )

    body = obj['body']

    need(
        type(body) is dict
        and set(body) == BODY_FIELDS,
        'invalid anchor fields'
    )

    need(
        body['format'] == FORMAT
        and body['non_value_research_only'] is True,
        'research domain mismatch'
    )

    need(
        type(body['chain_id']) is str
        and bool(
            gate.CHAIN.fullmatch(
                body['chain_id']
            )
        ),
        'invalid anchor chain'
    )

    need(
        type(body['sequence']) is int
        and 1 <= body['sequence'] <= gate.MAX_INT,
        'invalid anchor sequence'
    )

    need(
        all(
            type(body[k]) is str
            and gate.HEX.fullmatch(
                body[k]
            ) is not None

            for k in (
                'previous_sha256',
                'public_key_sha256',
                'messages_sha256',
                'state_sha256'
            )
        ),
        'invalid anchor hash'
    )

    need(
        body['public_key_sha256'] == pin,
        'anchor signer pin mismatch'
    )

    need(
        all(
            type(body[k]) is int
            and 1 <= body[k] <= gate.MAX_ROWS

            for k in (
                'message_count',
                'peer_count'
            )
        ),
        'invalid snapshot counts'
    )

    tips = body['tips']

    need(
        type(tips) is list
        and len(tips) == body['peer_count'],
        'invalid tips'
    )

    for tip in tips:
        need(
            type(tip) is list
            and len(tip) == 4
            and type(tip[0]) is str
            and bool(
                gate.NAME.fullmatch(
                    tip[0]
                )
            )
            and all(
                type(v) is int
                and 1 <= v <= gate.MAX_INT

                for v in tip[1:]
            ),
            'invalid tip'
        )

    need(
        tips == sorted(tips)
        and len({
            v[0] for v in tips
        }) == len(tips),
        'noncanonical tip order'
    )

    if body['sequence'] == 1:
        need(
            body['previous_sha256'] == ZERO,
            'genesis link mismatch'
        )

    else:
        need(
            body['previous_sha256'] != ZERO,
            'missing predecessor'
        )

    gate.b64decode(
        obj['signature_b64']
    )

    need(
        crypto(
            'verify',
            public_key,
            gate.canonical(body),
            obj['signature_b64']
        ) == 'VERIFIED',
        'invalid signer proof'
    )

    return body, gate.sha(raw)


def advance(
    previous,
    previous_hash,
    body,
    state
):
    need(
        body['chain_id'] == previous['chain_id']
        and body['sequence'] == (
            previous['sequence'] + 1
        )
        and body['previous_sha256'] == previous_hash,
        'wrong anchor chain or sequence'
    )

    n = previous['message_count']

    need(
        n <= len(state['messages'])
        and n <= body['message_count'],
        'rollback below externally anchored height'
    )

    old_tips = {
        t[0]: (
            t[1],
            t[2]
        )
        for t in previous['tips']
    }

    prefix = [
        m
        for m in state['messages']

        if m[0] in old_tips
        and (
            m[1] < old_tips[m[0]][0]

            or (
                m[1] == old_tips[m[0]][0]
                and m[2] <= old_tips[m[0]][1]
            )
        )
    ]

    need(
        len(prefix) == n
        and message_hash(
            state['chain_id'],
            prefix
        ) == previous['messages_sha256'],
        'anchored message prefix modified'
    )

    current = {
        t[0]: t[1:]
        for t in state['tips']
    }

    for (
        sender,
        epoch,
        counter,
        timestamp
    ) in previous['tips']:

        now = current.get(sender)

        need(
            now is not None
            and now[2] >= timestamp
            and (
                now[0] > epoch

                or (
                    now[0] == epoch
                    and now[1] >= counter
                )
            ),
            'anchored peer tip rolled back'
        )


def verify(
    ledger,
    anchor,
    public,
    pin,
    previous=None
):
    pub = check_pin(
        public,
        pin
    )

    body, anchor_hash = load_anchor(
        anchor,
        pub,
        pin
    )

    state = ledger_state(
        ledger,
        body['chain_id']
    )

    need(
        len(state['messages']) == body['message_count']
        and len(state['tips']) == body['peer_count']
        and state['tips'] == body['tips']
        and message_hash(
            body['chain_id'],
            state['messages']
        ) == body['messages_sha256']
        and state_hash(
            state
        ) == body['state_sha256'],
        'ROLLBACK_OR_TAMPER: ledger does not match independently retained anchor'
    )

    if previous is not None:
        old, old_hash = load_anchor(
            previous,
            pub,
            pin
        )

        advance(
            old,
            old_hash,
            body,
            state
        )

    return {
        'status':
            'EXACT_SIGNED_SNAPSHOT_MATCH',

        'chain_id':
            body['chain_id'],

        'sequence':
            body['sequence'],

        'message_count':
            body['message_count'],

        'anchor_sha256':
            anchor_hash,

        'externally_retained_proven':
            False,

        'non_value_research_only':
            True
    }


def capture(
    ledger,
    output,
    private,
    public,
    pin,
    chain,
    previous=None
):
    pub = check_pin(
        public,
        pin
    )

    prv = private_file(
        private,
        16384
    )

    probe = (
        b'AUNEYA/WVP v1.9 signing key self-check'
    )

    need(
        crypto(
            'verify',
            pub,
            probe,
            crypto(
                'sign',
                prv,
                probe
            )
        ) == 'VERIFIED',
        'signer private/public mismatch'
    )

    state = ledger_state(
        ledger,
        chain
    )

    previous_body = None
    previous_hash = ZERO
    sequence = 1

    if previous is not None:
        previous_body, previous_hash = load_anchor(
            previous,
            pub,
            pin
        )

        sequence = (
            previous_body['sequence'] + 1
        )

    body = {
        'format':
            FORMAT,

        'chain_id':
            chain,

        'sequence':
            sequence,

        'previous_sha256':
            previous_hash,

        'public_key_sha256':
            pin,

        'messages_sha256':
            message_hash(
                chain,
                state['messages']
            ),

        'state_sha256':
            state_hash(state),

        'message_count':
            len(state['messages']),

        'peer_count':
            len(state['tips']),

        'tips':
            state['tips'],

        'non_value_research_only':
            True
    }

    if previous_body is not None:
        advance(
            previous_body,
            previous_hash,
            body,
            state
        )

        need(
            body['message_count'] >
            previous_body['message_count'],
            'checkpoint must advance beyond previous height'
        )

    signature = crypto(
        'sign',
        prv,
        gate.canonical(body)
    )

    gate.b64decode(signature)

    raw = gate.canonical({
        'body':
            body,

        'signature_b64':
            signature
    }) + b'\n'

    need(
        len(raw) <= MAX_ANCHOR,
        'anchor too large'
    )

    target = Path(
        output
    ).absolute()

    gate.private_dir(
        target.parent
    )

    need(
        not target.is_symlink(),
        'refusing symlink'
    )

    fd = os.open(
        target,

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

    try:
        with os.fdopen(
            fd,
            'wb'
        ) as f:

            f.write(raw)
            f.flush()

            os.fsync(
                f.fileno()
            )

        folder = os.open(
            target.parent,
            os.O_RDONLY
        )

        try:
            os.fsync(folder)

        finally:
            os.close(folder)

    except BaseException:
        target.unlink(
            missing_ok=True
        )
        raise

    return verify(
        ledger,
        target,
        public,
        pin,
        previous
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    sub = parser.add_subparsers(
        dest='action',
        required=True
    )

    for name in (
        'capture',
        'verify'
    ):
        p = sub.add_parser(name)

        for key in (
            'ledger',
            'public',
            'pin'
        ):
            p.add_argument(
                '--' + key,
                required=True
            )

        p.add_argument(
            '--previous'
        )

        if name == 'capture':
            for key in (
                'output',
                'private',
                'chain'
            ):
                p.add_argument(
                    '--' + key,
                    required=True
                )

        else:
            p.add_argument(
                '--anchor',
                required=True
            )

    a = parser.parse_args()

    try:
        if a.action == 'capture':
            result = capture(
                a.ledger,
                a.output,
                a.private,
                a.public,
                a.pin,
                a.chain,
                a.previous
            )

        else:
            result = verify(
                a.ledger,
                a.anchor,
                a.public,
                a.pin,
                a.previous
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
        sqlite3.Error
    ) as exc:

        parser.exit(
            2,
            'FAIL-CLOSED: ' +
            str(exc) +
            '\n'
        )


if __name__ == '__main__':
    main()
