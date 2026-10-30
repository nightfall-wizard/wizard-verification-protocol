#!/usr/bin/env python3

"""
AUNEYA/WVP v1.5

Time-scoped local admission of independently
verified v1.4 portable evidence bundles.

Security boundaries:

- No historical freshness proof.
- No trusted-clock proof.
- No Sybil-resistance proof.
- No consensus proof.
- No token or mainnet activation.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]

VERIFIER = (
    ROOT /
    'tools/auneya/auneya_independent_v14.js'
)

HEX = set('0123456789abcdef')

MAX_MANIFEST = 128 * 1024
MAX_TOTAL = 8 * 1024 * 1024
MAX_ROWS = 50000
MAX_LAG = 600
SKEW = 30


class AdmissionError(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise AdmissionError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(s):
    return (
        isinstance(s, str)
        and len(s) == 64
        and all(c in HEX for c in s)
    )


def private_dir(path):
    p = Path(path)
    s = p.lstat()

    need(
        stat.S_ISDIR(s.st_mode)
        and not s.st_mode & 0o077,
        'directory must be private 0700'
    )

    return p


def read_private(path, bound):
    flags = (
        os.O_RDONLY |
        getattr(os, 'O_NOFOLLOW', 0)
    )

    fd = os.open(path, flags)

    try:
        s = os.fstat(fd)

        need(
            stat.S_ISREG(s.st_mode)
            and not s.st_mode & 0o077,
            'expected private regular 0600 file'
        )

        need(
            0 < s.st_size < bound,
            'file exceeds resource limit'
        )

        with os.fdopen(os.dup(fd), 'rb') as f:
            raw = f.read(bound)

        need(
            len(raw) == s.st_size
            and len(raw) < bound,
            'file changed during read'
        )

        return raw

    finally:
        os.close(fd)


def no_duplicates(items):
    obj = {}

    for k, v in items:
        need(
            k not in obj,
            'duplicate JSON key'
        )
        obj[k] = v

    return obj


def strict_json(raw):
    return json.loads(
        raw,
        object_pairs_hook=no_duplicates,
        parse_float=lambda x: (
            _ for _ in ()
        ).throw(
            AdmissionError('float')
        ),
        parse_constant=lambda x: (
            _ for _ in ()
        ).throw(
            AdmissionError('constant')
        )
    )


def inspect(
    bundle,
    pin,
    challenge_hash,
    manifest_hash,
    now
):
    need(
        all(
            map(
                digest,
                (
                    pin,
                    challenge_hash,
                    manifest_hash
                )
            )
        ),
        'three independent SHA256 anchors required'
    )

    need(
        type(now) is int
        and 0 <= now <= 2**63 - 1,
        'invalid verifier clock'
    )

    private_dir(bundle)
    private_dir(Path(bundle) / 'capsules')

    mraw = read_private(
        Path(bundle) / 'manifest.json',
        MAX_MANIFEST
    )

    need(
        sha(mraw) == manifest_hash,
        'manifest hash mismatch'
    )

    m = strict_json(mraw)

    need(
        type(m) is dict
        and m.get('format') ==
        'auneya-portable-federation-v1.2',
        'manifest format mismatch'
    )

    need(
        m.get('checkpoint_sha256') == pin
        and m.get('challenge_sha256')
        == challenge_hash,
        'manifest pin mismatch'
    )

    entries = m.get('capsules')

    need(
        type(entries) is list
        and 1 <= len(entries) <= 16,
        'capsule resource budget exceeded'
    )

    need(
        sorted(
            p.name
            for p in (
                Path(bundle) / 'capsules'
            ).iterdir()
        ) ==
        sorted(
            e['sha256'] + '.json'
            for e in entries
            if type(e) is dict
            and digest(e.get('sha256'))
        ),
        'unexpected capsule files'
    )

    budget = len(mraw)
    latest = None
    observed_count = 0

    for e in entries:
        need(
            type(e) is dict
            and set(e) == {
                'file',
                'sha256',
                'size_bytes'
            }
            and digest(e['sha256'])
            and e['file'] ==
            'capsules/' +
            e['sha256'] +
            '.json'
            and type(e['size_bytes']) is int
            and 0 < e['size_bytes']
            < 3 * 1024 * 1024,
            'invalid capsule entry'
        )

        budget += e['size_bytes']

        need(
            budget <= MAX_TOTAL,
            'bundle exceeds 8 MiB admission budget'
        )

        raw = read_private(
            Path(bundle) / e['file'],
            3 * 1024 * 1024
        )

        need(
            len(raw) == e['size_bytes']
            and sha(raw) == e['sha256'],
            'capsule changed since manifest pin'
        )

        cap = strict_json(raw)

        need(
            type(cap) is dict
            and type(
                cap.get('challenge')
            ) is dict
            and type(
                cap.get('receipts')
            ) is list,
            'invalid capsule'
        )

        c = cap['challenge']

        start = c.get('issued_at')
        end = c.get('expires_at')

        need(
            type(start) is int
            and type(end) is int
            and 0 <= start <= 2**63 - 1
            and 0 <= end <= 2**63 - 1
            and 1 <= end - start <= 600
            and sha(
                json.dumps(
                    c,
                    sort_keys=True,
                    ensure_ascii=True,
                    separators=(',', ':'),
                    allow_nan=False
                ).encode('ascii')
            ) == challenge_hash,
            'challenge mismatch'
        )

        need(
            start - SKEW <= now
            <= end + SKEW,
            'challenge outside local admission window'
        )

        latest = (
            end
            if latest is None
            else max(latest, end)
        )

        for receipt in cap['receipts']:
            need(
                type(receipt) is dict
                and type(
                    receipt.get('observed_at')
                ) is int,
                'invalid observation time'
            )

            t = receipt['observed_at']

            need(
                start - SKEW <= t
                <= end + SKEW
                and now - MAX_LAG <= t
                <= now + SKEW,
                'observation outside local admission window'
            )

            observed_count += 1

    need(
        observed_count >= 2,
        'missing signed observations'
    )

    return {
        'expires_at': latest,
        'observation_count': observed_count,
        'total_bytes': budget
    }


def safe_ledger(ledger):
    p = Path(ledger).absolute()

    private_dir(p.parent)

    try:
        fd = os.open(
            p,
            os.O_WRONLY |
            os.O_CREAT |
            os.O_EXCL |
            getattr(os, 'O_NOFOLLOW', 0),
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
        and s.st_size <= 16 * 1024 * 1024,
        'ledger must be bounded private regular 0600 file'
    )

    return p


def commit(
    ledger,
    challenge_hash,
    manifest_hash,
    now,
    expires_at
):
    p = safe_ledger(ledger)

    db = sqlite3.connect(
        p,
        timeout=15,
        isolation_level=None
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
                'CREATE TABLE IF NOT EXISTS accepted ('
                'challenge_sha256 TEXT PRIMARY KEY, '
                'manifest_sha256 TEXT NOT NULL UNIQUE, '
                'admitted_at INTEGER NOT NULL, '
                'expires_at INTEGER NOT NULL)'
            )

            db.execute(
                'CREATE TABLE IF NOT EXISTS state ('
                'name TEXT PRIMARY KEY, '
                'value INTEGER NOT NULL)'
            )

            row = db.execute(
                "SELECT value FROM state "
                "WHERE name='last_now'"
            ).fetchone()

            need(
                row is None
                or now >= row[0],
                'local clock rollback detected'
            )

            count, = db.execute(
                'SELECT COUNT(*) FROM accepted'
            ).fetchone()

            need(
                count < MAX_ROWS,
                'replay ledger reached capacity'
            )

            repeated = db.execute(
                'SELECT 1 FROM accepted '
                'WHERE challenge_sha256=? '
                'OR manifest_sha256=?',
                (
                    challenge_hash,
                    manifest_hash
                )
            ).fetchone()

            need(
                repeated is None,
                'REPLAY: challenge or manifest already admitted'
            )

            db.execute(
                'INSERT INTO accepted '
                'VALUES (?,?,?,?)',
                (
                    challenge_hash,
                    manifest_hash,
                    now,
                    expires_at
                )
            )

            db.execute(
                "INSERT INTO state "
                "VALUES ('last_now',?) "
                "ON CONFLICT(name) "
                "DO UPDATE SET value=excluded.value",
                (now,)
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

    except sqlite3.IntegrityError as exc:
        raise AdmissionError(
            'ledger integrity violation'
        ) from exc

    finally:
        db.close()


def admit(
    bundle,
    pin,
    challenge_hash,
    manifest_hash,
    ledger,
    now=None
):
    now = (
        int(time.time())
        if now is None
        else now
    )

    info = inspect(
        bundle,
        pin,
        challenge_hash,
        manifest_hash,
        now
    )

    try:
        result = subprocess.run(
            [
                'node',
                str(VERIFIER),
                'verify',
                '--bundle',
                str(bundle),
                '--pin',
                pin,
                '--challenge-sha256',
                challenge_hash,
                '--expected-manifest-sha256',
                manifest_hash
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            check=False
        )

    except (
        OSError,
        subprocess.TimeoutExpired
    ) as exc:
        raise AdmissionError(
            'v1.4 cryptographic verification unavailable'
        ) from exc

    need(
        result.returncode == 0,
        'v1.4 cryptographic verification rejected bundle: '
        + result.stderr.strip()[:250]
    )

    try:
        verified = json.loads(
            result.stdout
        )

    except json.JSONDecodeError as exc:
        raise AdmissionError(
            'unparseable v1.4 verifier output'
        ) from exc

    manifest_again = strict_json(
        read_private(
            Path(bundle) / 'manifest.json',
            MAX_MANIFEST
        )
    )

    need(
        verified.get('result') ==
        'PORTABLE_SIGNED_STATEMENTS_REVERIFIED'
        and verified.get(
            'manifest_sha256'
        ) == manifest_hash
        and verified.get(
            'capsule_count'
        ) == len(
            manifest_again['capsules']
        )
        and verified.get(
            'security_boundary', {}
        ).get(
            'consensus_validated'
        ) is False,
        'incorrect v1.4 verification result'
    )

    need(
        inspect(
            bundle,
            pin,
            challenge_hash,
            manifest_hash,
            now
        ) == info,
        'bundle changed during admission'
    )

    commit(
        ledger,
        challenge_hash,
        manifest_hash,
        now,
        info['expires_at']
    )

    return {
        'format':
            'auneya-temporal-admission-v1.5',
        'result':
            'LOCALLY_ADMITTED_ONCE',
        'manifest_sha256':
            manifest_hash,
        'challenge_sha256':
            challenge_hash,
        'admitted_at':
            now,
        'expires_at':
            info['expires_at'],
        'observation_count':
            info['observation_count'],
        'authenticated_statements_only':
            True,
        'trusted_time_proven':
            False,
        'sybil_resistance_proven':
            False,
        'consensus_validated':
            False,
        'non_value_research_only':
            True
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        'action',
        choices=['admit']
    )

    parser.add_argument(
        '--bundle',
        required=True,
        type=Path
    )

    parser.add_argument(
        '--pin',
        required=True
    )

    parser.add_argument(
        '--challenge-sha256',
        required=True
    )

    parser.add_argument(
        '--expected-manifest-sha256',
        required=True
    )

    parser.add_argument(
        '--ledger',
        required=True,
        type=Path
    )

    args = parser.parse_args()

    try:
        print(
            json.dumps(
                admit(
                    args.bundle,
                    args.pin,
                    args.challenge_sha256,
                    args.expected_manifest_sha256,
                    args.ledger
                ),
                sort_keys=True,
                indent=2
            )
        )

    except (
        AdmissionError,
        OSError,
        sqlite3.DatabaseError,
        TypeError,
        KeyError,
        ValueError
    ) as exc:
        parser.exit(
            2,
            'FAIL-CLOSED: ' + str(exc) + '\n'
        )


if __name__ == '__main__':
    main()
