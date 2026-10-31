#!/usr/bin/env python3

"""
AUNEYA v1.10

Offline independent high-water witness.

Run on a separate storage/rollback domain
for meaningful external retention.

No public networking.
No trusted time.
No Sybil resistance.
No economic activity.
"""

import argparse
import json
import os
from pathlib import Path
import sqlite3
import stat

import auneya_anchor_v19 as anchor
import auneya_peer_gate_v16 as gate


FORMAT = (
    'auneya-independent-highwater-receipt-v1.10'
)

DOMAIN = (
    b'AUNEYA/WVP:INDEPENDENT-HIGHWATER:V1.10\x00'
)

ZERO = '0' * 64

MAX_DB = 32 * 1024 * 1024
MAX_RECEIPT = 16 * 1024

FIELDS = {
    'format',
    'chain_id',
    'sequence',
    'anchor_sha256',
    'previous_anchor_sha256',
    'anchor_signer_sha256',
    'witness_public_key_sha256',
    'previous_receipt_sha256',
    'message_count',
    'peer_count',
    'tips_sha256',
    'non_value_research_only'
}


class WitnessError(ValueError):
    pass


def need(ok, reason):

    if not ok:
        raise WitnessError(reason)


def canonical(obj):

    return gate.canonical(obj)


def digest(buf):

    return gate.sha(buf)


def receipt_bytes(body, private_key):

    sig = anchor.crypto(
        'sign',
        private_key,
        DOMAIN + canonical(body)
    )

    gate.b64decode(sig)

    return canonical({
        'body': body,
        'signature_b64': sig
    }) + b'\n'


def inspect_receipt(
    path,
    witness_public,
    witness_pin
):

    raw = gate.read_private(
        path,
        MAX_RECEIPT
    )

    need(
        raw.endswith(b'\n')
        and raw.count(b'\n') == 1,
        'invalid receipt framing'
    )

    obj = gate.strict_json(raw[:-1])

    need(
        type(obj) is dict
        and set(obj) == {
            'body',
            'signature_b64'
        }
        and canonical(obj) + b'\n' == raw,
        'noncanonical receipt'
    )

    b = obj['body']

    need(
        type(b) is dict
        and set(b) == FIELDS,
        'invalid receipt fields'
    )

    need(
        b['format'] == FORMAT
        and b['non_value_research_only'] is True,
        'incorrect research domain'
    )

    need(
        type(b['chain_id']) is str
        and gate.CHAIN.fullmatch(b['chain_id']),
        'invalid chain identifier'
    )

    need(
        type(b['sequence']) is int
        and 1 <= b['sequence'] <= gate.MAX_INT,
        'invalid receipt sequence'
    )

    need(
        type(b['message_count']) is int
        and 1 <= b['message_count'] <= gate.MAX_ROWS,
        'invalid message count'
    )

    need(
        type(b['peer_count']) is int
        and 1 <= b['peer_count'] <= gate.MAX_ROWS,
        'invalid peer count'
    )

    for f in (
        'anchor_sha256',
        'previous_anchor_sha256',
        'anchor_signer_sha256',
        'witness_public_key_sha256',
        'previous_receipt_sha256',
        'tips_sha256'
    ):

        need(
            type(b[f]) is str
            and gate.HEX.fullmatch(b[f]),
            'invalid digest field: ' + f
        )

    need(
        b['witness_public_key_sha256'] == witness_pin,
        'witness pin mismatch'
    )

    need(
        b['sequence'] != 1
        or (
            b['previous_anchor_sha256'] == ZERO
            and b['previous_receipt_sha256'] == ZERO
        ),
        'invalid genesis witness links'
    )

    gate.b64decode(
        obj['signature_b64']
    )

    need(
        anchor.crypto(
            'verify',
            witness_public,
            DOMAIN + canonical(b),
            obj['signature_b64']
        ) == 'VERIFIED',
        'forged witness receipt'
    )

    return b, digest(raw), raw


def check_store(path):

    p = Path(path).absolute()

    gate.private_dir(p.parent)

    if not p.exists():

        need(
            not p.is_symlink(),
            'store symlink refused'
        )

        fd = os.open(
            p,
            os.O_CREAT
            | os.O_EXCL
            | os.O_WRONLY
            | getattr(os, 'O_NOFOLLOW', 0),
            0o600
        )

        os.close(fd)

    st = p.lstat()

    need(
        stat.S_ISREG(st.st_mode)
        and st.st_nlink == 1
        and not st.st_mode & 0o077
        and st.st_size <= MAX_DB,
        'private bounded 0600 keeper store required'
    )

    return p


def open_store(path):

    p = check_store(path)

    db = sqlite3.connect(
        str(p),
        timeout=8,
        isolation_level=None
    )

    db.execute(
        'PRAGMA busy_timeout=8000'
    )

    db.execute(
        'PRAGMA journal_mode=DELETE'
    )

    db.execute(
        'PRAGMA synchronous=FULL'
    )

    need(
        db.execute(
            'PRAGMA quick_check'
        ).fetchone() == ('ok',),
        'keeper store damaged'
    )

    db.execute('''
        CREATE TABLE IF NOT EXISTS highwater (
            chain TEXT PRIMARY KEY,
            anchor_pin TEXT NOT NULL,
            witness_pin TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            anchor_hash TEXT NOT NULL,
            receipt BLOB NOT NULL,
            message_count INTEGER NOT NULL,
            tips TEXT NOT NULL
        )
    ''')

    return db


def put_file_new(path, raw):

    p = Path(path).absolute()

    gate.private_dir(p.parent)

    need(
        not p.is_symlink(),
        'receipt symlink refused'
    )

    fd = os.open(
        p,
        os.O_CREAT
        | os.O_EXCL
        | os.O_WRONLY
        | getattr(os, 'O_NOFOLLOW', 0),
        0o600
    )

    try:

        with os.fdopen(fd, 'wb') as out:

            out.write(raw)
            out.flush()

            os.fsync(
                out.fileno()
            )

        d = os.open(
            p.parent,
            os.O_RDONLY
        )

        try:
            os.fsync(d)

        finally:
            os.close(d)

    except BaseException:

        p.unlink(
            missing_ok=True
        )

        raise


def validate_bindings(
    body,
    anchor_body,
    anchor_sha,
    anchor_pin,
    witness_pin
):

    need(
        body['chain_id'] == anchor_body['chain_id']
        and body['sequence'] == anchor_body['sequence']
        and body['anchor_sha256'] == anchor_sha
        and body['previous_anchor_sha256']
            == anchor_body['previous_sha256']
        and body['anchor_signer_sha256'] == anchor_pin
        and body['witness_public_key_sha256']
            == witness_pin
        and body['message_count']
            == anchor_body['message_count']
        and body['peer_count']
            == anchor_body['peer_count']
        and body['tips_sha256']
            == digest(canonical(anchor_body['tips'])),
        'receipt/anchor mismatch'
    )


def verify(
    anchor_path,
    receipt_path,
    anchor_pub,
    anchor_pin,
    witness_pub,
    witness_pin,
    previous_receipt=None
):

    need(
        anchor_pin != witness_pin,
        'separate signer identities required'
    )

    apub = anchor.check_pin(
        anchor_pub,
        anchor_pin
    )

    wpub = anchor.check_pin(
        witness_pub,
        witness_pin
    )

    ab, ahash = anchor.load_anchor(
        anchor_path,
        apub,
        anchor_pin
    )

    rb, rhash, _ = inspect_receipt(
        receipt_path,
        wpub,
        witness_pin
    )

    validate_bindings(
        rb,
        ab,
        ahash,
        anchor_pin,
        witness_pin
    )

    if previous_receipt:

        pb, phash, _ = inspect_receipt(
            previous_receipt,
            wpub,
            witness_pin
        )

        need(
            rb['sequence'] == pb['sequence'] + 1
            and rb['previous_receipt_sha256'] == phash
            and rb['previous_anchor_sha256']
                == pb['anchor_sha256']
            and rb['chain_id'] == pb['chain_id'],
            'witness receipt chain rollback/fork'
        )

    return {
        'status':
            'SIGNED_OFFLINE_WITNESS_RECEIPT',

        'chain_id':
            rb['chain_id'],

        'sequence':
            rb['sequence'],

        'anchor_sha256':
            ahash,

        'receipt_sha256':
            rhash,

        'independent_device_proven':
            False,

        'externally_retained_proven':
            False,

        'non_value_research_only':
            True
    }


def accept(
    store,
    anchor_path,
    anchor_pub,
    anchor_pin,
    witness_private,
    witness_pub,
    witness_pin,
    output,
    previous_receipt=None
):

    need(
        anchor_pin != witness_pin,
        'separate signer identities required'
    )

    apub = anchor.check_pin(
        anchor_pub,
        anchor_pin
    )

    wpub = anchor.check_pin(
        witness_pub,
        witness_pin
    )

    wpriv = anchor.private_file(
        witness_private,
        16384
    )

    probe = DOMAIN + b'key-pair-check'

    try:

        pair_ok = (
            anchor.crypto(
                'verify',
                wpub,
                probe,
                anchor.crypto(
                    'sign',
                    wpriv,
                    probe
                )
            ) == 'VERIFIED'
        )

    except ValueError as exc:

        raise WitnessError(
            'witness key pair mismatch'
        ) from exc

    need(
        pair_ok,
        'witness key pair mismatch'
    )

    ab, ahash = anchor.load_anchor(
        anchor_path,
        apub,
        anchor_pin
    )

    pbody = None
    phash = ZERO

    if previous_receipt:

        pbody, phash, _ = inspect_receipt(
            previous_receipt,
            wpub,
            witness_pin
        )

    dest = Path(output).absolute()

    gate.private_dir(
        dest.parent
    )

    need(
        not dest.exists()
        and not dest.is_symlink(),
        'receipt destination already exists'
    )

    db = open_store(store)

    try:

        db.execute(
            'BEGIN IMMEDIATE'
        )

        row = db.execute(
            'SELECT '
            'anchor_pin,witness_pin,sequence,anchor_hash,'
            'receipt,message_count,tips '
            'FROM highwater WHERE chain=?',

            (ab['chain_id'],)
        ).fetchone()

        if row is None:

            need(
                pbody is None
                and ab['sequence'] == 1,
                'missing previous keeper state / illegal restart'
            )

            prior_receipt_hash = ZERO

        else:

            (
                old_ap,
                old_wp,
                old_seq,
                old_hash,
                old_receipt,
                old_count,
                old_tips
            ) = row

            need(
                old_ap == anchor_pin
                and old_wp == witness_pin,
                'keeper identity changed'
            )

            need(
                pbody is not None
                and phash == digest(old_receipt)
                and old_receipt == gate.read_private(
                    previous_receipt,
                    MAX_RECEIPT
                ),
                'external high-water receipt mismatch / store rollback'
            )

            need(
                pbody['chain_id'] == ab['chain_id']
                and pbody['anchor_sha256'] == old_hash
                and pbody['sequence'] == old_seq,
                'client high-water contradicts keeper'
            )

            need(
                ab['sequence'] == old_seq + 1
                and ab['previous_sha256'] == old_hash
                and ab['message_count'] > old_count,
                'noncontiguous checkpoint or rolled-back history'
            )

            old = json.loads(
                old_tips
            )

            new = {
                t[0]: tuple(t[1:])
                for t in ab['tips']
            }

            for (
                sender,
                epoch,
                counter,
                ts
            ) in old:

                current = new.get(sender)

                need(
                    current is not None
                    and current[2] >= ts
                    and (
                        current[0] > epoch
                        or (
                            current[0] == epoch
                            and current[1] >= counter
                        )
                    ),
                    'peer high-water regressed'
                )

            prior_receipt_hash = phash

        rb = {
            'format':
                FORMAT,

            'chain_id':
                ab['chain_id'],

            'sequence':
                ab['sequence'],

            'anchor_sha256':
                ahash,

            'previous_anchor_sha256':
                ab['previous_sha256'],

            'anchor_signer_sha256':
                anchor_pin,

            'witness_public_key_sha256':
                witness_pin,

            'previous_receipt_sha256':
                prior_receipt_hash,

            'message_count':
                ab['message_count'],

            'peer_count':
                ab['peer_count'],

            'tips_sha256':
                digest(canonical(ab['tips'])),

            'non_value_research_only':
                True
        }

        data = receipt_bytes(
            rb,
            wpriv
        )

        need(
            len(data) <= MAX_RECEIPT,
            'receipt too large'
        )

        db.execute(
            'INSERT OR REPLACE INTO highwater '
            'VALUES(?,?,?,?,?,?,?,?)',

            (
                ab['chain_id'],
                anchor_pin,
                witness_pin,
                ab['sequence'],
                ahash,
                data,
                ab['message_count'],
                canonical(
                    ab['tips']
                ).decode('ascii')
            )
        )

        # Commit before exporting the receipt.
        # Interrupted exports are recoverable.

        db.execute(
            'COMMIT'
        )

        put_file_new(
            dest,
            data
        )

    except BaseException:

        if db.in_transaction:
            db.execute('ROLLBACK')

        raise

    finally:

        db.close()

    return verify(
        anchor_path,
        dest,
        anchor_pub,
        anchor_pin,
        witness_pub,
        witness_pin,
        previous_receipt
    )


def export_receipt(
    store,
    chain,
    witness_pub,
    witness_pin,
    output,
    expected_floor=None
):

    p = Path(store).absolute()

    need(
        p.is_file()
        and not p.is_symlink(),
        'keeper store missing'
    )

    wpub = anchor.check_pin(
        witness_pub,
        witness_pin
    )

    floor = None

    if expected_floor:

        floor, _, _ = inspect_receipt(
            expected_floor,
            wpub,
            witness_pin
        )

    db = open_store(p)

    try:

        row = db.execute(
            'SELECT witness_pin,sequence,anchor_hash,receipt '
            'FROM highwater WHERE chain=?',

            (chain,)
        ).fetchone()

        need(
            row is not None,
            'chain absent in keeper store'
        )

        (
            wp,
            seq,
            ahash,
            data
        ) = row

        need(
            wp == witness_pin,
            'keeper signing identity changed'
        )

        need(
            data.endswith(b'\n'),
            'corrupt keeper receipt framing'
        )

        obj = gate.strict_json(
            data[:-1]
        )

        need(
            gate.canonical(obj) + b'\n' == data,
            'corrupt keeper receipt'
        )

        body = obj['body']

        need(
            body['chain_id'] == chain
            and body['sequence'] == seq
            and body['anchor_sha256'] == ahash
            and body['witness_public_key_sha256']
                == witness_pin
            and anchor.crypto(
                'verify',
                wpub,
                DOMAIN + canonical(body),
                obj['signature_b64']
            ) == 'VERIFIED',
            'keeper database receipt signature mismatch'
        )

        if floor:

            need(
                floor['chain_id'] == chain
                and floor['sequence'] == seq
                and floor['anchor_sha256'] == ahash
                and digest(
                    gate.read_private(
                        expected_floor,
                        MAX_RECEIPT
                    )
                ) == digest(data),
                'keeper database below outside receipt floor'
            )

    finally:

        db.close()

    put_file_new(
        output,
        data
    )

    return {
        'status':
            'OFFLINE_KEEPER_RECEIPT_EXPORTED',

        'sequence':
            seq,

        'chain_id':
            chain,

        'receipt_sha256':
            digest(data),

        'independent_device_proven':
            False,

        'non_value_research_only':
            True
    }


def main():

    p = argparse.ArgumentParser(
        description=__doc__
    )

    sub = p.add_subparsers(
        dest='op',
        required=True
    )

    for action in (
        'accept',
        'verify',
        'export'
    ):

        a = sub.add_parser(action)

        if action == 'export':

            for key in (
                'store',
                'chain',
                'witness-public',
                'witness-pin',
                'output'
            ):

                a.add_argument(
                    '--' + key,
                    required=True
                )

            a.add_argument(
                '--expected-floor'
            )

            continue

        for key in (
            'anchor',
            'anchor-public',
            'anchor-pin',
            'witness-public',
            'witness-pin'
        ):

            a.add_argument(
                '--' + key,
                required=True
            )

        a.add_argument(
            '--previous-receipt'
        )

        if action == 'accept':

            for key in (
                'store',
                'witness-private',
                'output'
            ):

                a.add_argument(
                    '--' + key,
                    required=True
                )

        else:

            a.add_argument(
                '--receipt',
                required=True
            )

    args = p.parse_args()

    try:

        if args.op == 'accept':

            result = accept(
                args.store,
                args.anchor,
                args.anchor_public,
                args.anchor_pin,
                args.witness_private,
                args.witness_public,
                args.witness_pin,
                args.output,
                args.previous_receipt
            )

        elif args.op == 'export':

            result = export_receipt(
                args.store,
                args.chain,
                args.witness_public,
                args.witness_pin,
                args.output,
                args.expected_floor
            )

        else:

            result = verify(
                args.anchor,
                args.receipt,
                args.anchor_public,
                args.anchor_pin,
                args.witness_public,
                args.witness_pin,
                args.previous_receipt
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
    ) as e:

        p.exit(
            2,
            'FAIL-CLOSED: ' + str(e) + '\n'
        )


if __name__ == '__main__':
    main()
