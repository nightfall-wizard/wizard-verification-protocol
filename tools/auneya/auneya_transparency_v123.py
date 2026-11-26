#!/usr/bin/env python3
"""AUNEYA v1.23: bounded, private evidence transparency journal.

Each append re-runs the genuine v1.22 dual-runtime cryptographic
verifier. Merkle inclusion proves membership in a pinned root,
NOT factual truth, independent devices or external retention.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

FORMAT = 'auneya-evidence-transparency-v1.23'
PROOF = 'auneya-inclusion-proof-v1.23'
MAX_ENTRIES = 256
MAX_JOURNAL = 512 * 1024
HEX = re.compile(r'[0-9a-f]{64}\Z')
CHAIN = re.compile(r'[a-zA-Z0-9._:-]{1,128}\Z')
DEC = re.compile(r'(0|[1-9][0-9]{0,18})\Z')

KEYS = (
    'chain_id',
    'sequence_decimal',
    'recipient_pin',
    'capsule_sha256',
    'ack_sha256',
    'floor_sha256',
    'anchor_sha256',
    'report_sha256',
)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def no_dupes(pairs):
    obj = {}
    for k, v in pairs:
        require(k not in obj, 'duplicate JSON key')
        obj[k] = v
    return obj


def canonical(obj):
    return (
        json.dumps(
            obj,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=True,
            allow_nan=False
        ) + '\n'
    ).encode('ascii')


def parse(raw):
    require(len(raw) <= MAX_JOURNAL, 'JSON too large')
    try:
        obj = json.loads(
            raw.decode('ascii'),
            object_pairs_hook=no_dupes,
            parse_constant=lambda _: (
                _ for _ in ()
            ).throw(ValueError('non-finite'))
        )
    except (UnicodeError, ValueError) as exc:
        raise ValueError('malformed JSON') from exc

    require(raw == canonical(obj), 'noncanonical JSON')
    return obj


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest_ok(value):
    return (
        type(value) is str
        and HEX.fullmatch(value) is not None
    )


def valid_record(rec):
    require(
        type(rec) is dict and set(rec) == set(KEYS),
        'record fields invalid'
    )
    require(
        type(rec['chain_id']) is str
        and CHAIN.fullmatch(rec['chain_id']),
        'chain invalid'
    )
    require(
        type(rec['sequence_decimal']) is str
        and DEC.fullmatch(rec['sequence_decimal']),
        'sequence invalid'
    )
    require(
        0 < int(rec['sequence_decimal']) <= 2**63 - 1,
        'sequence range'
    )
    for k in KEYS[2:]:
        require(
            digest_ok(rec[k]),
            'invalid commitment: ' + k
        )


def node(left, right):
    return hashlib.sha256(
        b'\x01'
        + bytes.fromhex(left)
        + bytes.fromhex(right)
    ).hexdigest()


def leaf(rec):
    valid_record(rec)
    return hashlib.sha256(
        b'\x00' + canonical(rec)
    ).hexdigest()


def split(n):
    require(n > 1, 'invalid tree size')
    return 1 << ((n - 1).bit_length() - 1)


def root(hashes):
    if not hashes:
        return sha(b'')
    if len(hashes) == 1:
        return hashes[0]

    k = split(len(hashes))
    return node(
        root(hashes[:k]),
        root(hashes[k:])
    )


def audit_path(hashes, idx):
    require(
        0 <= idx < len(hashes),
        'index out of bounds'
    )
    if len(hashes) == 1:
        return []

    k = split(len(hashes))

    if idx < k:
        return audit_path(
            hashes[:k], idx
        ) + [{
            'side': 'right',
            'hash': root(hashes[k:])
        }]

    return audit_path(
        hashes[k:], idx - k
    ) + [{
        'side': 'left',
        'hash': root(hashes[:k])
    }]


def empty():
    return {
        'format': FORMAT,
        'entries': [],
        'root_sha256': root([])
    }


def validate(journal):
    require(
        type(journal) is dict
        and set(journal) == {
            'format',
            'entries',
            'root_sha256'
        },
        'journal fields invalid'
    )

    require(
        journal['format'] == FORMAT,
        'unknown journal format'
    )

    records = journal['entries']

    require(
        type(records) is list
        and len(records) <= MAX_ENTRIES,
        'invalid journal size'
    )

    for i, rec in enumerate(records):
        valid_record(rec)

        if i:
            previous = records[i - 1]

            require(
                rec['chain_id'] == previous['chain_id']
                and rec['recipient_pin']
                == previous['recipient_pin'],
                'journal identity changed'
            )

            require(
                int(rec['sequence_decimal'])
                == int(previous['sequence_decimal']) + 1,
                'non-contiguous sequence'
            )

    hashes = [leaf(x) for x in records]

    require(
        digest_ok(journal['root_sha256'])
        and journal['root_sha256'] == root(hashes),
        'journal root mismatch'
    )

    return hashes


def private_parent(path):
    path = Path(path).absolute()
    parent = path.parent

    require(
        parent.is_dir() and not parent.is_symlink(),
        'private parent directory required'
    )

    mode = parent.stat().st_mode

    require(
        mode & 0o077 == 0,
        'parent directory must be mode 0700'
    )

    require(
        not path.is_symlink(),
        'symlink path refused'
    )

    return path


def safe_read(path, *, max_bytes=MAX_JOURNAL):
    require(type(max_bytes) is int and 1 <= max_bytes <= MAX_JOURNAL,
            'invalid input budget')
    path = private_parent(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
                 | getattr(os, 'O_CLOEXEC', 0))
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                and 0 < before.st_size <= max_bytes,
                'not a bounded regular file')
        raw = bytearray()
        while len(raw) <= before.st_size:
            part = os.read(fd, min(65536, before.st_size + 1 - len(raw)))
            if not part:
                break
            raw.extend(part)
        after = os.fstat(fd)
        fields = ('st_dev', 'st_ino', 'st_size', 'st_nlink',
                  'st_mtime_ns', 'st_ctime_ns')
        require(len(raw) == before.st_size and stat.S_ISREG(after.st_mode)
                and all(getattr(before, k) == getattr(after, k) for k in fields),
                'concurrent input mutation')
        return parse(bytes(raw))
    finally:
        os.close(fd)


def atomic_write(path, data, overwrite):
    path = private_parent(path)

    require(
        len(data) <= MAX_JOURNAL,
        'output exceeds bound'
    )

    if not overwrite:
        fd = os.open(
            path,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | os.O_NOFOLLOW,
            0o600
        )

        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)

    else:
        fd, tmp = tempfile.mkstemp(
            prefix='.auneya-v123-',
            dir=path.parent
        )

        try:
            os.fchmod(fd, 0o600)
            os.write(fd, data)
            os.fsync(fd)
            os.close(fd)
            fd = -1

            require(
                not path.is_symlink(),
                'journal was replaced by symlink'
            )

            os.replace(tmp, path)

        finally:
            if fd >= 0:
                os.close(fd)

            if os.path.exists(tmp):
                os.unlink(tmp)

    dfd = os.open(
        path.parent, os.O_RDONLY
    )

    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


@contextlib.contextmanager
def lock_for(path):
    path = private_parent(path)
    lock = path.with_name(
        path.name + '.lock'
    )

    fd = os.open(
        lock,
        os.O_RDWR
        | os.O_CREAT
        | os.O_NOFOLLOW,
        0o600
    )

    try:
        st = os.fstat(fd)

        require(
            stat.S_ISREG(st.st_mode)
            and st.st_nlink == 1,
            'lock file invalid'
        )

        fcntl.flock(
            fd, fcntl.LOCK_EX
        )

        yield

    finally:
        fcntl.flock(
            fd, fcntl.LOCK_UN
        )
        os.close(fd)


def init(path):
    with lock_for(path):
        atomic_write(
            path,
            canonical(empty()),
            overwrite=False
        )

    return empty()


def append_record(path, record):
    valid_record(record)

    with lock_for(path):
        state = safe_read(path)
        validate(state)

        require(
            len(state['entries']) < MAX_ENTRIES,
            'full journal'
        )

        state['entries'].append(record)

        state['root_sha256'] = root([
            leaf(x)
            for x in state['entries']
        ])

        validate(state)

        atomic_write(
            path,
            canonical(state),
            overwrite=True
        )

    return {
        'size': len(state['entries']),
        'root_sha256': state['root_sha256']
    }


def record_from_report(report):
    require(
        type(report) is dict
        and report.get('format')
        == 'auneya-gate3-fieldtrial-offline-v1.22',
        'not a v1.22 report'
    )

    for key in (
        'python_quorum_verified',
        'node_quorum_verified',
        'python_ack_verified',
        'node_ack_verified',
        'inputs_unchanged'
    ):
        require(
            report.get(key) is True,
            'unverified v1.22 status'
        )

    for key in (
        'independent_devices_proven',
        'external_retention_proven',
        'economic_activation',
        'mainnet_active'
    ):
        require(
            report.get(key) is False,
            'unsafe claim in v1.22 result'
        )

    result = {
        k: report[k]
        for k in KEYS
        if k != 'report_sha256'
    }

    result['report_sha256'] = sha(
        canonical(report)
    )

    valid_record(result)
    return result


def append_verified(path, args):
    # Re-run real Ed25519 checks.
    # Supplied standalone reports are not trusted.

    from types import SimpleNamespace
    import auneya_fieldtrial_v122 as trial

    keys = (
        'trust',
        'capsule',
        'ack',
        'floor',
        'recipient_public',
        'recipient_pin',
        'expected_trust',
        'expected_capsule',
        'expected_ack',
        'expected_floor'
    )

    report = trial.run(
        SimpleNamespace(**{
            k: getattr(args, k)
            for k in keys
        })
    )

    return append_record(
        path,
        record_from_report(report)
    )


def prove(journal, idx):
    hashes = validate(journal)

    require(
        0 <= idx < len(hashes),
        'invalid proof index'
    )

    return {
        'format': PROOF,
        'size': len(hashes),
        'index': idx,
        'record': journal['entries'][idx],
        'path': audit_path(hashes, idx),
        'root_sha256': journal['root_sha256']
    }


def verify_proof(p, expected_root, expected_size):
    require(
        type(p) is dict
        and set(p) == {
            'format',
            'size',
            'index',
            'record',
            'path',
            'root_sha256'
        },
        'invalid proof fields'
    )

    require(
        p['format'] == PROOF
        and type(p['size']) is int
        and type(p['index']) is int
        and 1 <= p['size'] <= MAX_ENTRIES
        and 0 <= p['index'] < p['size']
        and type(p['path']) is list
        and len(p['path']) <= 9,
        'proof shape invalid'
    )

    require(
        digest_ok(expected_root)
        and expected_root == p['root_sha256']
        and p['size'] == expected_size,
        'independent root or size mismatch'
    )

    h = leaf(p['record'])

    n = p['size']
    i = p['index']

    expected_sides = []

    while n > 1:
        k = split(n)

        if i < k:
            expected_sides.append('right')
            n = k
        else:
            expected_sides.append('left')
            i -= k
            n -= k

    expected_sides.reverse()

    require(
        len(expected_sides) == len(p['path']),
        'wrong path length'
    )

    for step, side in zip(
        p['path'],
        expected_sides
    ):
        require(
            type(step) is dict
            and set(step) == {'side', 'hash'}
            and step['side'] == side
            and digest_ok(step['hash']),
            'wrong path topology'
        )

        if side == 'left':
            h = node(
                step['hash'], h
            )
        else:
            h = node(
                h, step['hash']
            )

    require(
        h == expected_root,
        'inclusion check failed'
    )

    return True


def compare_history(
    old,
    new,
    old_root,
    new_root
):
    validate(old)
    validate(new)

    require(
        old['root_sha256'] == old_root
        and new['root_sha256'] == new_root
        and digest_ok(old_root)
        and digest_ok(new_root),
        'external head mismatch'
    )

    require(
        len(old['entries'])
        <= len(new['entries']),
        'history truncated'
    )

    require(
        old['entries']
        == new['entries'][:len(old['entries'])],
        'history fork detected'
    )

    return {
        'status': 'PREFIX_CONSISTENT',
        'old_size': len(old['entries']),
        'new_size': len(new['entries']),
        'new_root_sha256': new_root,
        'independent_retention_proven': False
    }


def main():
    p = argparse.ArgumentParser(
        description=__doc__
    )

    sub = p.add_subparsers(
        dest='action',
        required=True
    )

    for name in (
        'init',
        'append',
        'inspect',
        'prove'
    ):
        s = sub.add_parser(name)

        s.add_argument(
            '--journal',
            required=True
        )

        if name == 'append':
            for k in (
                'trust',
                'capsule',
                'ack',
                'floor',
                'recipient-public',
                'recipient-pin',
                'expected-trust',
                'expected-capsule',
                'expected-ack',
                'expected-floor'
            ):
                s.add_argument(
                    '--' + k,
                    required=True
                )

        if name == 'prove':
            s.add_argument(
                '--index',
                required=True,
                type=int
            )

            s.add_argument(
                '--out',
                required=True
            )

    s = sub.add_parser(
        'verify-proof'
    )

    s.add_argument(
        '--proof',
        required=True
    )
    s.add_argument(
        '--expected-root',
        required=True
    )
    s.add_argument(
        '--expected-size',
        required=True,
        type=int
    )

    s = sub.add_parser('compare')

    for k in (
        'old',
        'new',
        'old-root',
        'new-root'
    ):
        s.add_argument(
            '--' + k,
            required=True
        )

    args = p.parse_args()

    if args.action == 'init':
        obj = init(args.journal)

    elif args.action == 'append':
        obj = append_verified(
            args.journal, args
        )

    elif args.action == 'inspect':
        journal = safe_read(
            args.journal
        )
        validate(journal)

        obj = {
            'size': len(journal['entries']),
            'root_sha256': journal['root_sha256']
        }

    elif args.action == 'prove':
        obj = prove(
            safe_read(args.journal),
            args.index
        )

        atomic_write(
            args.out,
            canonical(obj),
            overwrite=False
        )

    elif args.action == 'verify-proof':
        obj = safe_read(
            args.proof
        )

        verify_proof(
            obj,
            args.expected_root,
            args.expected_size
        )

        obj = {
            'status': 'INCLUDED_IN_PINNED_ROOT',
            'independent_retention_proven': False
        }

    else:
        obj = compare_history(
            safe_read(args.old),
            safe_read(args.new),
            args.old_root,
            args.new_root
        )

    sys.stdout.buffer.write(
        canonical(obj)
    )


if __name__ == '__main__':
    try:
        main()
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        ImportError
    ) as exc:
        sys.exit(
            'REJECTED: ' + str(exc)
        )
