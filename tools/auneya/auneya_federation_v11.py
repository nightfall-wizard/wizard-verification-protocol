#!/usr/bin/env python3

"""
AUNEYA/WVP v1.1

Offline federation of independently pinned v0.9 capsules.

Authenticates signed statements, not their real-world
truth or physical operator independence.
"""

import argparse
from collections import defaultdict
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat

import auneya_archive_v09 as v9
import auneya_nightfall_challenge_v05 as v5
import auneya_registry_checkpoint_v06 as v6

FORMAT = 'auneya-offline-federation-v1.1'
MAX_CAPSULE = 3 * 1024 * 1024
MAX_CAPSULES_PER_EVENT = 16


class FederationError(ValueError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hex64(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in '0123456789abcdef' for c in value)
    )


def private_file(path):
    p = Path(path).absolute()

    fd = os.open(
        str(p),
        os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    )

    with os.fdopen(fd, 'rb') as f:
        mode = os.fstat(f.fileno())

        if (
            not stat.S_ISREG(mode.st_mode)
            or mode.st_mode & 0o077
        ):
            raise FederationError(
                'capsule must be private regular file (0600)'
            )

        if mode.st_size < 1 or mode.st_size >= MAX_CAPSULE:
            raise FederationError('capsule size rejected')

        raw = f.read(MAX_CAPSULE)

    if len(raw) >= MAX_CAPSULE:
        raise FederationError('capsule oversized')

    return raw


def parse_capsule(raw, pin, challenge_hash):

    if not hex64(pin) or not hex64(challenge_hash):
        raise FederationError(
            'independent pin and challenge hash required'
        )

    if not isinstance(raw, bytes) or len(raw) >= MAX_CAPSULE:
        raise FederationError('oversized capsule')

    obj = json.loads(
        raw,
        object_pairs_hook=v5.pairs,
        parse_constant=lambda _: (
            _ for _ in ()
        ).throw(FederationError('nonfinite JSON'))
    )

    if raw != v6.canonical(obj):
        raise FederationError('noncanonical evidence capsule')

    # Existing cryptographic verification.
    finding = v9.inspect(obj, pin)

    if sha(v5.canonical(obj['challenge'])) != challenge_hash:
        raise FederationError('unexpected challenge identity')

    if finding['result'] != 'OFFLINE_SIGNED_STATEMENTS_AUTHENTIC':
        raise FederationError('unexpected evidence class')

    return obj


def db_path(path, create):

    p = Path(path).absolute()

    if p.is_symlink() or not p.parent.is_dir():
        raise FederationError('unsafe database path')

    if p.exists():
        s = p.stat()

        if (
            not stat.S_ISREG(s.st_mode)
            or s.st_mode & 0o077
        ):
            raise FederationError(
                'database must be private regular file (0600)'
            )

    elif not create:
        raise FederationError('database missing')

    return p


def connect(path, create=False):

    p = db_path(path, create)

    old = os.umask(0o077)

    try:
        db = sqlite3.connect(str(p), timeout=10)
    finally:
        os.umask(old)

    if p.stat().st_mode & 0o077:
        db.close()
        raise FederationError('unsafe database permissions')

    db.execute('PRAGMA busy_timeout=10000')
    db.execute('PRAGMA synchronous=FULL')

    return db


def schema(db):

    db.execute(
        'CREATE TABLE IF NOT EXISTS federation_capsules_v11 ('
        'capsule_sha256 TEXT PRIMARY KEY, '
        'challenge_sha256 TEXT NOT NULL, '
        'pin_sha256 TEXT NOT NULL, '
        'payload BLOB NOT NULL)'
    )

    db.execute(
        'CREATE INDEX IF NOT EXISTS federation_event_v11 '
        'ON federation_capsules_v11('
        'challenge_sha256, pin_sha256)'
    )


def ingest(store, capsule, pin, challenge_hash):

    raw = private_file(capsule)

    # Verify before opening the persistence transaction.
    parse_capsule(raw, pin, challenge_hash)

    path = db_path(store, True)

    if (
        path == Path(capsule).absolute()
        or (
            path.exists()
            and os.path.samefile(path, capsule)
        )
    ):
        raise FederationError('database aliases capsule')

    cap_hash = sha(raw)

    with closing(connect(path, True)) as db:

        db.execute('BEGIN IMMEDIATE')

        try:
            schema(db)

            conflicting = db.execute(
                'SELECT 1 FROM federation_capsules_v11 '
                'WHERE challenge_sha256=? '
                'AND pin_sha256<>? LIMIT 1',
                (challenge_hash, pin)
            ).fetchone()

            if conflicting:
                raise FederationError(
                    'different independent pin for same challenge'
                )

            count = db.execute(
                'SELECT count(*) FROM federation_capsules_v11 '
                'WHERE challenge_sha256=?',
                (challenge_hash,)
            ).fetchone()[0]

            row = db.execute(
                'SELECT 1 FROM federation_capsules_v11 '
                'WHERE capsule_sha256=?',
                (cap_hash,)
            ).fetchone()

            if row:
                db.commit()

                return {
                    'result': 'ALREADY_IMPORTED',
                    'capsule_sha256': cap_hash,
                    'challenge_sha256': challenge_hash,
                    'non_value_research_only': True
                }

            if count >= MAX_CAPSULES_PER_EVENT:
                raise FederationError(
                    'event archive limit exceeded'
                )

            db.execute(
                'INSERT INTO federation_capsules_v11 '
                'VALUES (?,?,?,?)',
                (
                    cap_hash,
                    challenge_hash,
                    pin,
                    sqlite3.Binary(raw)
                )
            )

            db.commit()

        except BaseException:
            db.rollback()
            raise

    return {
        'result': 'IMPORTED_AND_AUTHENTICATED',
        'capsule_sha256': cap_hash,
        'challenge_sha256': challenge_hash,
        'non_value_research_only': True
    }


def report(store, pin, challenge_hash):

    if not hex64(pin) or not hex64(challenge_hash):
        raise FederationError('invalid independent identifiers')

    with closing(connect(store)) as db:

        rows = db.execute(
            'SELECT capsule_sha256, pin_sha256, payload '
            'FROM federation_capsules_v11 '
            'WHERE challenge_sha256=? '
            'ORDER BY capsule_sha256',
            (challenge_hash,)
        ).fetchall()

        foreign = db.execute(
            'SELECT 1 FROM federation_capsules_v11 '
            'WHERE challenge_sha256=? '
            'AND pin_sha256<>? LIMIT 1',
            (challenge_hash, pin)
        ).fetchone()

    if foreign:
        raise FederationError(
            'archive contains conflicting checkpoint pins'
        )

    if not rows or len(rows) > MAX_CAPSULES_PER_EVENT:
        raise FederationError(
            'no bounded archived evidence for challenge'
        )

    names = defaultdict(dict)
    fingerprints = {}
    capsule_hashes = []

    for cap_hash, stored_pin, raw in rows:

        if stored_pin != pin or sha(raw) != cap_hash:
            raise FederationError('database archive corruption')

        obj = parse_capsule(raw, pin, challenge_hash)

        capsule_hashes.append(cap_hash)

        for receipt in obj['receipts']:

            name = receipt['node_id']

            # Public key binding is verified by v9.inspect.
            fp = sha(bytes.fromhex(obj['keys'][name]))

            if (
                name in fingerprints
                and fingerprints[name] != fp
            ):
                raise FederationError('signer key mismatch')

            fingerprints[name] = fp

            receipt_hash = sha(v5.canonical(receipt))

            names[name][receipt_hash] = receipt

    by_fp = defaultdict(list)

    for name, fp in fingerprints.items():
        by_fp[fp].append(name)

    aliases = [
        sorted(a)
        for a in by_fp.values()
        if len(a) > 1
    ]

    equivocators = sorted(
        name
        for name, values in names.items()
        if len({
            sha(v5.canonical(r['status']))
            for r in values.values()
        }) > 1
    )

    samples = [
        r
        for entries in names.values()
        for r in entries.values()
    ]

    states = defaultdict(set)

    for r in samples:

        s = r['status']

        state_id = (
            s['tip_height'],
            s['tip'],
            s['total_work']
        )

        states[state_id].add(r['node_id'])

    if aliases:
        verdict = 'DUPLICATE_PUBLIC_KEY_IDENTITIES'

    elif equivocators:
        verdict = 'SAME_SIGNER_CONTRADICTORY_STATEMENTS'

    elif len(states) == 1:
        verdict = 'MATCHING_SIGNED_TIP_CLAIMS'

    elif len({state[0] for state in states}) < len(states):
        verdict = 'CONFLICTING_SAME_HEIGHT_SIGNED_CLAIMS'

    else:
        verdict = 'DIVERGENT_SIGNED_CLAIMS_NOT_FORK_PROOF'

    commitment = {
        'format': FORMAT,
        'challenge_sha256': challenge_hash,
        'checkpoint_sha256': pin,
        'capsule_sha256': sorted(capsule_hashes)
    }

    return {
        'format': FORMAT,
        'result': 'AUTHENTICATED_ARCHIVED_STATEMENTS_ONLY',
        'observation_verdict': verdict,
        'archive_count': len(rows),
        'distinct_key_count': len(by_fp),
        'signer_identity_count': len(names),
        'unique_signed_statement_count': len(samples),
        'equivocating_signer_ids': equivocators,
        'duplicate_public_key_identities': sorted(aliases),
        'claimed_tip_groups': [
            {
                'tip_height': h,
                'tip': tip,
                'total_work': work,
                'signed_by': sorted(ids)
            }
            for (h, tip, work), ids
            in sorted(states.items())
        ],
        'federation_sha256': sha(v5.canonical(commitment)),
        'historical_freshness_proven': False,
        'operator_independence_proven': False,
        'consensus_validated': False,
        'non_value_research_only': True
    }


def main():

    ap = argparse.ArgumentParser(description=__doc__)

    sub = ap.add_subparsers(
        dest='cmd',
        required=True
    )

    for name in ('import', 'report'):

        p = sub.add_parser(name)

        p.add_argument('--store', required=True)

        p.add_argument(
            '--pin',
            required=True,
            help='Independently retained checkpoint SHA-256'
        )

        p.add_argument(
            '--challenge-sha256',
            required=True
        )

        if name == 'import':
            p.add_argument('--capsule', required=True)

    a = ap.parse_args()

    try:

        if a.cmd == 'import':
            result = ingest(
                a.store,
                a.capsule,
                a.pin,
                a.challenge_sha256
            )
        else:
            result = report(
                a.store,
                a.pin,
                a.challenge_sha256
            )

        print(json.dumps(result, indent=2, sort_keys=True))

    except (
        ValueError,
        KeyError,
        TypeError,
        IndexError,
        OSError,
        sqlite3.Error,
        OverflowError,
        RecursionError
    ) as e:

        ap.exit(
            2,
            'FAIL-CLOSED: ' + str(e) + '\n'
        )


if __name__ == '__main__':
    main()
