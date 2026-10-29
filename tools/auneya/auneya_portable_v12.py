#!/usr/bin/env python3

"""
AUNEYA/WVP v1.2

Portable, independently rechecked
offline federation evidence.
"""

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import tempfile

import auneya_federation_v11 as v11
import auneya_nightfall_challenge_v05 as v5
import auneya_registry_checkpoint_v06 as v6


FORMAT = 'auneya-portable-federation-v1.2'

MAX_MANIFEST = 128 * 1024

BOUNDARIES = {
    'authenticated_signed_statements_only': True,
    'consensus_validated': False,
    'historical_freshness_proven': False,
    'operator_independence_proven': False,
    'sybil_resistance_proven': False,
    'mainnet_active': False,
    'transferable_value_created': False,
}


class PortableError(ValueError):
    pass


def require(condition, message):

    if not condition:
        raise PortableError(message)


def private_directory(path):

    p = Path(path).absolute()
    s = p.lstat()

    require(
        stat.S_ISDIR(s.st_mode)
        and not (s.st_mode & 0o077),
        'directory must be private (0700), not a symlink'
    )

    return p


def read_private(path, maximum):

    fd = os.open(
        str(path),
        os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    )

    with os.fdopen(fd, 'rb') as f:

        s = os.fstat(f.fileno())

        require(
            stat.S_ISREG(s.st_mode)
            and not (s.st_mode & 0o077),
            'input must be private regular file (0600)'
        )

        require(
            0 < s.st_size < maximum,
            'invalid file size'
        )

        raw = f.read(maximum)

    require(
        0 < len(raw) < maximum,
        'file too large or empty'
    )

    return raw


def write_new(path, data):

    fd = os.open(
        str(path),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600
    )

    with os.fdopen(fd, 'wb') as f:

        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def parse_manifest(raw):

    obj = json.loads(
        raw,
        object_pairs_hook=v5.pairs,
        parse_constant=lambda _: (
            _ for _ in ()
        ).throw(
            PortableError('nonfinite JSON')
        )
    )

    require(
        isinstance(obj, dict)
        and raw == v6.canonical(obj),
        'manifest must be canonical JSON'
    )

    require(
        set(obj) == {
            'format',
            'checkpoint_sha256',
            'challenge_sha256',
            'capsules',
            'federation_report',
            'security_boundary'
        },
        'unexpected manifest fields'
    )

    require(
        obj['format'] == FORMAT
        and obj['security_boundary'] == BOUNDARIES,
        'wrong format or security claims'
    )

    return obj


def rebuild(capsules, pin, challenge_hash, scratch):

    """
    Reuse the actual v1.1 cryptographic
    verifier, not only file hashes.
    """

    db = scratch / 'rechecked.sqlite'

    for index, (digest, raw) in enumerate(capsules):

        require(
            v11.sha(raw) == digest,
            'capsule digest mismatch'
        )

        v11.parse_capsule(
            raw,
            pin,
            challenge_hash
        )

        f = scratch / ('input-%02d.json' % index)

        write_new(f, raw)

        v11.ingest(
            db,
            f,
            pin,
            challenge_hash
        )

    return v11.report(
        db,
        pin,
        challenge_hash
    )


def verify(
    bundle,
    pin,
    challenge_hash,
    expected_manifest_hash
):

    require(
        all(
            v11.hex64(x)
            for x in (
                pin,
                challenge_hash,
                expected_manifest_hash
            )
        ),
        'three independently supplied SHA-256 values required'
    )

    root = private_directory(bundle)

    require(
        {p.name for p in root.iterdir()} == {
            'manifest.json',
            'capsules'
        },
        'unexpected or missing top-level bundle files'
    )

    capdir = private_directory(
        root / 'capsules'
    )

    raw = read_private(
        root / 'manifest.json',
        MAX_MANIFEST
    )

    require(
        v11.sha(raw) == expected_manifest_hash,
        'externally pinned manifest digest mismatch'
    )

    obj = parse_manifest(raw)

    require(
        obj['checkpoint_sha256'] == pin
        and obj['challenge_sha256'] == challenge_hash,
        'independent pin or challenge mismatch'
    )

    entries = obj['capsules']

    require(
        isinstance(entries, list)
        and 1 <= len(entries)
        <= v11.MAX_CAPSULES_PER_EVENT,
        'capsule count out of bounds'
    )

    found = set()
    digests = []
    capsules = []

    for item in entries:

        require(
            isinstance(item, dict)
            and set(item) == {
                'file',
                'sha256',
                'size_bytes'
            },
            'invalid capsule manifest entry'
        )

        digest = item['sha256']

        require(
            v11.hex64(digest)
            and item['file']
            == 'capsules/' + digest + '.json',
            'unsafe capsule filename or hash'
        )

        require(
            type(item['size_bytes']) is int
            and 0 < item['size_bytes']
            < v11.MAX_CAPSULE,
            'invalid capsule size declaration'
        )

        require(
            digest not in found,
            'duplicate capsule reference'
        )

        found.add(digest)
        digests.append(digest)

        payload = read_private(
            capdir / (digest + '.json'),
            v11.MAX_CAPSULE
        )

        require(
            len(payload) == item['size_bytes'],
            'capsule length mismatch'
        )

        capsules.append(
            (digest, payload)
        )

    require(
        digests == sorted(digests),
        'noncanonical capsule ordering'
    )

    require(
        {p.name for p in capdir.iterdir()}
        == {x + '.json' for x in found},
        'missing or unexpected capsule file'
    )

    with tempfile.TemporaryDirectory(
        prefix='auneya-v12-verify-'
    ) as tmp:

        result = rebuild(
            capsules,
            pin,
            challenge_hash,
            Path(tmp)
        )

    require(
        result == obj['federation_report'],
        'archived federation report does not reproduce'
    )

    return {
        'result':
            'PORTABLE_SIGNED_STATEMENTS_REVERIFIED',

        'manifest_sha256':
            expected_manifest_hash,

        'capsule_count':
            len(capsules),

        'federation_sha256':
            result['federation_sha256'],

        'observation_verdict':
            result['observation_verdict'],

        'security_boundary':
            BOUNDARIES
    }


def export(
    store,
    pin,
    challenge_hash,
    output
):

    require(
        v11.hex64(pin)
        and v11.hex64(challenge_hash),
        'external checkpoint and challenge hashes required'
    )

    out = Path(output).absolute()

    require(
        not os.path.lexists(str(out)),
        'output already exists'
    )

    private_directory(out.parent)

    with closing(v11.connect(store)) as db:

        # One consistent SQLite snapshot.
        db.execute('BEGIN')

        rows = db.execute(
            'SELECT capsule_sha256, pin_sha256, payload '
            'FROM federation_capsules_v11 '
            'WHERE challenge_sha256=? '
            'ORDER BY capsule_sha256',
            (challenge_hash,)
        ).fetchall()

        foreign = db.execute(
            'SELECT 1 '
            'FROM federation_capsules_v11 '
            'WHERE challenge_sha256=? '
            'AND pin_sha256<>? LIMIT 1',
            (challenge_hash, pin)
        ).fetchone()

        db.rollback()

    require(
        not foreign
        and 1 <= len(rows)
        <= v11.MAX_CAPSULES_PER_EVENT,
        'absent, conflicting or excessive archived capsules'
    )

    capsules = []

    for digest, stored_pin, raw in rows:

        require(
            stored_pin == pin
            and v11.hex64(digest),
            'untrusted database entry'
        )

        payload = bytes(raw)

        require(
            0 < len(payload)
            < v11.MAX_CAPSULE,
            'oversized database capsule'
        )

        capsules.append(
            (digest, payload)
        )

    stage = None

    try:

        with tempfile.TemporaryDirectory(
            prefix='auneya-v12-build-'
        ) as tmp:

            report = rebuild(
                capsules,
                pin,
                challenge_hash,
                Path(tmp)
            )

        stage = Path(
            tempfile.mkdtemp(
                prefix='.auneya-v12-',
                dir=out.parent
            )
        )

        capdir = stage / 'capsules'
        capdir.mkdir(mode=0o700)

        entries = []

        for digest, payload in capsules:

            filename = digest + '.json'

            write_new(
                capdir / filename,
                payload
            )

            entries.append({
                'file': 'capsules/' + filename,
                'sha256': digest,
                'size_bytes': len(payload)
            })

        manifest = {
            'format': FORMAT,
            'checkpoint_sha256': pin,
            'challenge_sha256': challenge_hash,
            'capsules': entries,
            'federation_report': report,
            'security_boundary': BOUNDARIES
        }

        manifest_raw = v6.canonical(
            manifest
        )

        require(
            len(manifest_raw) < MAX_MANIFEST,
            'manifest too large'
        )

        write_new(
            stage / 'manifest.json',
            manifest_raw
        )

        digest = v11.sha(
            manifest_raw
        )

        # Rebuild and reverify before publication.
        verify(
            stage,
            pin,
            challenge_hash,
            digest
        )

        require(
            not os.path.lexists(str(out)),
            'output path appeared'
        )

        os.rename(
            stage,
            out
        )

        stage = None

        return {
            'result':
                'EXPORTED_AND_LOCALLY_REVERIFIED',

            'bundle':
                str(out),

            'manifest_sha256':
                digest,

            'capsule_count':
                len(capsules),

            'federation_sha256':
                report['federation_sha256'],

            'security_boundary':
                BOUNDARIES
        }

    finally:

        if stage is not None:
            shutil.rmtree(stage)


def main():

    ap = argparse.ArgumentParser(
        description=__doc__
    )

    sub = ap.add_subparsers(
        dest='command',
        required=True
    )

    for name in ('export', 'verify'):

        p = sub.add_parser(name)

        p.add_argument(
            '--pin',
            required=True
        )

        p.add_argument(
            '--challenge-sha256',
            required=True
        )

        if name == 'export':

            p.add_argument(
                '--store',
                required=True
            )

            p.add_argument(
                '--out',
                required=True
            )

        else:

            p.add_argument(
                '--bundle',
                required=True
            )

            p.add_argument(
                '--expected-manifest-sha256',
                required=True
            )

    args = ap.parse_args()

    try:

        if args.command == 'export':

            result = export(
                args.store,
                args.pin,
                args.challenge_sha256,
                args.out
            )

        else:

            result = verify(
                args.bundle,
                args.pin,
                args.challenge_sha256,
                args.expected_manifest_sha256
            )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True
            )
        )

    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        sqlite3.Error,
        OverflowError,
        RecursionError
    ) as exc:

        ap.exit(
            2,
            'FAIL-CLOSED: ' + str(exc) + '\n'
        )


if __name__ == '__main__':
    main()
