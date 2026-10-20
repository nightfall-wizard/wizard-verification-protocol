#!/usr/bin/env python3
"""AUNEYA v0.6: read-only, externally pinned v0.4 registry checkpoints.

Research only. Protect the current checkpoint SHA-256 OUTSIDE the database's
security domain. A local attacker who controls both can still forge/rollback.
"""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import sys
from urllib.parse import quote

FORMAT = 'auneya-registry-checkpoint-v0.6'
HEX = re.compile(r'^[0-9a-f]{64}$')
MAX_DB = 32 * 1024 * 1024
MAX_SEAL = 2 * 1024 * 1024
MAX_ROWS = 20000
SCHEMA = {
    'nodes': ['node_id', 'epoch', 'fingerprint', 'public_der', 'state'],
    'events': ['node_id', 'epoch', 'event_digest', 'kind'],
}


class CheckpointError(ValueError):
    pass


def fail(message):
    raise CheckpointError(message)


def canonical(data):
    return (json.dumps(data, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def strict_pairs(items):
    data = {}
    for key, value in items:
        if key in data:
            fail('duplicate JSON key')
        data[key] = value
    return data


def regular_private(path, maximum):
    path = Path(path)
    try:
        mode = path.lstat()
    except OSError as exc:
        raise CheckpointError('missing/unreadable private input') from exc
    if not stat.S_ISREG(mode.st_mode) or mode.st_mode & 0o077:
        fail('input must be a private regular file (0600, no symlink)')
    if mode.st_size > maximum:
        fail('oversized input')
    return path


def read_seal(path, expected):
    if not isinstance(expected, str) or not HEX.fullmatch(expected):
        fail('expected SHA-256 pin must be exactly 64 lowercase hex characters')
    raw = regular_private(path, MAX_SEAL).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        fail('CHECKPOINT PIN MISMATCH')
    try:
        body = json.loads(raw, object_pairs_hook=strict_pairs,
                          parse_float=lambda _: fail('floating point forbidden'),
                          parse_constant=lambda _: fail('nonfinite forbidden'))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise CheckpointError('invalid checkpoint JSON') from exc
    if not isinstance(body, dict) or set(body) != {'format', 'previous', 'nodes', 'events'}:
        fail('checkpoint schema mismatch')
    if body['format'] != FORMAT or body['previous'] is not None and (
            not isinstance(body['previous'], str) or not HEX.fullmatch(body['previous'])):
        fail('checkpoint format/previous invalid')
    if canonical(body) != raw:
        fail('checkpoint must have canonical encoding')
    validate_snapshot(body)
    return body


def validate_snapshot(body):
    ns, es = body['nodes'], body['events']
    if not isinstance(ns, list) or not isinstance(es, list):
        fail('snapshot arrays required')
    if not ns or len(ns) > MAX_ROWS or len(es) > MAX_ROWS:
        fail('snapshot row limits')
    nodes = {}
    for n in ns:
        if not isinstance(n, dict) or set(n) != {'id', 'epoch', 'fingerprint', 'state'}:
            fail('invalid node schema')
        ident, epoch, fp, state = n['id'], n['epoch'], n['fingerprint'], n['state']
        if not isinstance(ident, str) or not 1 <= len(ident) <= 128 or '\x00' in ident:
            fail('invalid identity')
        if type(epoch) is not int or not 0 <= epoch <= MAX_ROWS:
            fail('invalid node epoch')
        if not isinstance(fp, str) or not HEX.fullmatch(fp) or state not in ('active', 'revoked'):
            fail('invalid node key or state')
        if ident in nodes:
            fail('duplicate node')
        nodes[ident] = n
    histories = {k: [] for k in nodes}
    for e in es:
        if not isinstance(e, dict) or set(e) != {'id', 'epoch', 'digest', 'kind'}:
            fail('invalid event schema')
        i = e['id']
        if i not in histories or type(e['epoch']) is not int:
            fail('orphan / invalid event')
        if not isinstance(e['digest'], str) or not HEX.fullmatch(e['digest']):
            fail('invalid event digest')
        if e['kind'] not in ('enroll', 'rotate', 'revoke'):
            fail('invalid event kind')
        histories[i].append(e)
    for i, n in nodes.items():
        events = sorted(histories[i], key=lambda e: e['epoch'])
        if len(events) != n['epoch'] + 1 or events[0]['kind'] != 'enroll':
            fail('incomplete identity history')
        if any(e['epoch'] != j or (j and e['kind'] == 'enroll') for j, e in enumerate(events)):
            fail('noncontiguous epochs / re-enrollment')
        if any(e['kind'] == 'revoke' for e in events[:-1]):
            fail('event after revocation')
        if (events[-1]['kind'] == 'revoke') != (n['state'] == 'revoked'):
            fail('revocation state mismatch')
    if ns != sorted(ns, key=lambda n: n['id']):
        fail('noncanonical node ordering')
    if es != sorted(es, key=lambda e: (e['id'], e['epoch'])):
        fail('noncanonical event ordering')


def snapshot(db_path):
    db_path = regular_private(db_path, MAX_DB).absolute()
    # SQLite online backup includes uncheckpointed WAL state, unlike raw file hashing.
    url = 'file:' + quote(str(db_path), safe='/') + '?mode=ro'
    try:
        with closing(sqlite3.connect(url, uri=True, timeout=5)) as source:
            source.execute('PRAGMA query_only=ON')
            with closing(sqlite3.connect(':memory:')) as copy:
                source.backup(copy, pages=50, sleep=0.02)
                if copy.execute('PRAGMA integrity_check').fetchone() != ('ok',):
                    fail('SQLite integrity check failed')
                for table, columns in SCHEMA.items():
                    actual = [r[1] for r in copy.execute('PRAGMA table_info(' + table + ')')]
                    if actual != columns:
                        fail('unknown registry schema: ' + table)
                nc = copy.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
                ec = copy.execute('SELECT COUNT(*) FROM events').fetchone()[0]
                if not 1 <= nc <= MAX_ROWS or not 1 <= ec <= MAX_ROWS:
                    fail('registry row limits')
                nodes = []
                for ident, epoch, fp, der, state in copy.execute(
                        'SELECT node_id,epoch,fingerprint,public_der,state FROM nodes ORDER BY node_id'):
                    if not isinstance(der, bytes) or len(der) != 44 or not der.startswith(
                            bytes.fromhex('302a300506032b6570032100')):
                        fail('invalid Ed25519 SPKI DER')
                    if not isinstance(fp, str) or hashlib.sha256(der).hexdigest() != fp:
                        fail('public-key fingerprint mismatch')
                    nodes.append(dict(id=ident, epoch=epoch, fingerprint=fp, state=state))
                events = [dict(id=i, epoch=ep, digest=d, kind=k) for i, ep, d, k in
                          copy.execute('SELECT node_id,epoch,event_digest,kind FROM events ORDER BY node_id,epoch')]
    except sqlite3.Error as exc:
        raise CheckpointError('SQLite read failed: ' + str(exc)) from exc
    body = {'format': FORMAT, 'previous': None, 'nodes': nodes, 'events': events}
    validate_snapshot(body)
    return body


def verify(db_path, seal_path, pin):
    old = read_seal(seal_path, pin)
    current = snapshot(db_path)
    for key in ('nodes', 'events'):
        if old[key] != current[key]:
            fail('REGISTRY STATE DIFFERS FROM PINNED CHECKPOINT')
    return old


def advance(db_path, seal_path, pin):
    old = read_seal(seal_path, pin)
    new = snapshot(db_path)
    on = {n['id']: n for n in old['nodes']}
    nn = {n['id']: n for n in new['nodes']}
    if not set(on) <= set(nn):
        fail('identity deletion or rollback')
    oe = {(e['id'], e['epoch']): e for e in old['events']}
    ne = {(e['id'], e['epoch']): e for e in new['events']}
    if any(ne.get(key) != value for key, value in oe.items()):
        fail('event deletion/rewrite/rollback')
    for ident, prior in on.items():
        nxt = nn[ident]
        if prior['state'] == 'revoked' and nxt != prior:
            fail('revoked identity changed')
        if nxt['epoch'] < prior['epoch']:
            fail('identity epoch rollback')
        if nxt['epoch'] == prior['epoch'] and nxt != prior:
            fail('identity rewritten without new event')
        if nxt['epoch'] > prior['epoch']:
            added = [ne[(ident, i)]['kind'] for i in range(prior['epoch'] + 1, nxt['epoch'] + 1)]
            if nxt['fingerprint'] != prior['fingerprint'] and 'rotate' not in added:
                fail('fingerprint rewritten without rotation')
    new['previous'] = pin
    return new


def write_new(path, body):
    p = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(str(p), flags, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            raw = canonical(body)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(p, 0o600)
        return hashlib.sha256(raw).hexdigest()
    except BaseException:
        p.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    for action in ('init', 'verify', 'advance'):
        cmd = subs.add_parser(action)
        cmd.add_argument('--registry', required=True)
        if action != 'init':
            cmd.add_argument('--seal', required=True)
            cmd.add_argument('--expected-sha256', required=True)
        if action != 'verify':
            cmd.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        if args.action == 'init':
            state = snapshot(args.registry)
        elif args.action == 'verify':
            verify(args.registry, args.seal, args.expected_sha256)
            print('PASS: registry equals externally pinned checkpoint')
            return 0
        else:
            state = advance(args.registry, args.seal, args.expected_sha256)
        digest = write_new(args.out, state)
        print('CHECKPOINT_SHA256=' + digest)
        print('Store this hash independently from the registry and checkpoint files.')
        return 0
    except (CheckpointError, OSError, TypeError, IndexError, KeyError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
