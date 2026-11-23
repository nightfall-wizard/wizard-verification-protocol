#!/usr/bin/env python3
"""AUNEYA v1.24: bounded RFC 9162-style offline Merkle consistency.

Extends the v1.23 tree WITHOUT asserting independent external retention.
Verification requires separately obtained prior/new size and root pins.
"""
import argparse
import sys

import auneya_transparency_v123 as journal

FORMAT = 'auneya-merkle-consistency-v1.24'
MAX_PATH = 9  # ceil(log2(256)) + 1 per RFC 9162


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def subproof(old_size, hashes, complete):
    """RFC 9162 section 2.1.4.1 minimal consistency path."""
    size = len(hashes)
    require(0 < old_size <= size, 'invalid subproof size')
    if old_size == size:
        return [] if complete else [journal.root(hashes)]
    k = journal.split(size)
    if old_size <= k:
        return subproof(old_size, hashes[:k], complete) + [
            journal.root(hashes[k:])
        ]
    return subproof(old_size - k, hashes[k:], False) + [
        journal.root(hashes[:k])
    ]


def generate(state, old_size, independently_pinned_old_root):
    leaves = journal.validate(state)
    new_size = len(leaves)
    require(type(old_size) is int and 1 <= old_size <= new_size,
            'old size invalid or journal empty')
    require(journal.digest_ok(independently_pinned_old_root),
            'old root pin invalid')
    old_root = journal.root(leaves[:old_size])
    require(old_root == independently_pinned_old_root,
            'old pinned tree does not match this journal prefix')
    path = subproof(old_size, leaves, True) if old_size < new_size else []
    require(len(path) <= MAX_PATH, 'consistency path too long')
    proof = {
        'format': FORMAT,
        'old_size': old_size,
        'new_size': new_size,
        'old_root_sha256': old_root,
        'new_root_sha256': state['root_sha256'],
        'path': path,
    }
    verify(proof, old_root, state['root_sha256'], old_size, new_size)
    return proof


def verify(proof, old_root, new_root, old_size, new_size):
    require(type(proof) is dict and set(proof) == {
        'format', 'old_size', 'new_size', 'old_root_sha256',
        'new_root_sha256', 'path'
    }, 'proof fields invalid')
    require(proof['format'] == FORMAT, 'proof format invalid')
    require(type(old_size) is int and type(new_size) is int
            and 1 <= old_size <= new_size <= journal.MAX_ENTRIES,
            'pinned tree sizes invalid')
    require(type(proof['old_size']) is int
            and type(proof['new_size']) is int
            and proof['old_size'] == old_size
            and proof['new_size'] == new_size,
            'proof sizes differ from external pins')
    require(journal.digest_ok(old_root) and journal.digest_ok(new_root)
            and proof['old_root_sha256'] == old_root
            and proof['new_root_sha256'] == new_root,
            'proof roots differ from external pins')
    path = proof['path']
    require(type(path) is list and len(path) <= MAX_PATH
            and all(journal.digest_ok(item) for item in path),
            'malformed consistency path')
    if old_size == new_size:
        require(not path and old_root == new_root,
                'equal-size history has conflicting roots or nonempty path')
    else:
        require(bool(path), 'missing consistency path')
        # RFC 9162 sec 2.1.4.2; prepend known root for power-of-two old size.
        chain = ([old_root] if old_size & (old_size - 1) == 0 else []) + path
        fn, sn = old_size - 1, new_size - 1
        while fn & 1:
            fn >>= 1
            sn >>= 1
        first = second = chain[0]
        for peer in chain[1:]:
            require(sn != 0, 'extra consistency node')
            if fn & 1 or fn == sn:
                first = journal.node(peer, first)
                second = journal.node(peer, second)
                while fn != 0 and not (fn & 1):
                    fn >>= 1
                    sn >>= 1
            else:
                second = journal.node(second, peer)
            fn >>= 1
            sn >>= 1
        require(sn == 0 and first == old_root and second == new_root,
                'fork, truncation, or invalid consistency proof')
    return {
        'status': 'PREFIX_CONSISTENT',
        'old_size': old_size,
        'new_size': new_size,
        'independent_retention_proven': False,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest='action', required=True)
    create = sub.add_parser('prove')
    create.add_argument('--journal', required=True)
    create.add_argument('--old-size', required=True, type=int)
    create.add_argument('--expected-old-root', required=True)
    create.add_argument('--out', required=True)
    check = sub.add_parser('verify')
    check.add_argument('--proof', required=True)
    for name in ('old', 'new'):
        check.add_argument('--expected-' + name + '-root', required=True)
        check.add_argument('--expected-' + name + '-size', required=True,
                           type=int)
    args = cli.parse_args()
    if args.action == 'prove':
        result = generate(journal.safe_read(args.journal), args.old_size,
                          args.expected_old_root)
        journal.atomic_write(args.out, journal.canonical(result), False)
        result = {'status': 'PROOF_WRITTEN', 'path_nodes': len(result['path']),
                  'independent_retention_proven': False}
    else:
        result = verify(journal.safe_read(args.proof),
                        args.expected_old_root, args.expected_new_root,
                        args.expected_old_size, args.expected_new_size)
    sys.stdout.buffer.write(journal.canonical(result))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, TypeError, KeyError) as exc:
        sys.exit('REJECTED: ' + str(exc))
