#!/usr/bin/env python3
"""AUNEYA v0.7: verify v0.5 observations against an externally pinned v0.6 snapshot.

Local research. No consensus validation, operator-independence proof or mainnet write.
"""
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
from urllib.parse import quote

import auneya_nightfall_challenge_v05 as observations
import auneya_registry_checkpoint_v06 as checkpoints
import auneya_trusted_node_identity_v04 as identities


class PinnedError(ValueError):
    pass


def snapshot_copy(registry, destination):
    """Take one read-only SQLite backup, including committed WAL transactions."""
    source_path = checkpoints.regular_private(registry, checkpoints.MAX_DB).absolute()
    uri = 'file:' + quote(str(source_path), safe='/') + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as source:
        source.execute('PRAGMA query_only=ON')
        with closing(sqlite3.connect(str(destination), timeout=5)) as target:
            source.backup(target, pages=50, sleep=0.02)
    destination.chmod(0o600)
    return checkpoints.snapshot(destination)


def ensure_not_input(replay_db, registry, seal):
    out = Path(replay_db).absolute()
    for critical in (registry, seal):
        source = Path(critical).absolute()
        if out == source:
            raise PinnedError('replay ledger must not overwrite registry or seal')
        if out.exists() and source.exists() and os.path.samefile(out, source):
            raise PinnedError('replay ledger aliases protected input')


def verify_pinned(challenge, receipts, registry, seal, expected_sha256, replay_db, now=None):
    """Fail closed before the existing v0.5 replay ledger is consumed."""
    if len(receipts) not in (1, 2):
        raise PinnedError('one or two receipts required')
    ensure_not_input(replay_db, registry, seal)
    trusted = checkpoints.read_seal(seal, expected_sha256)
    now = int(time.time()) if now is None else now

    with tempfile.TemporaryDirectory(prefix='auneya-v07-frozen-') as folder:
        frozen_path = Path(folder) / 'registry.sqlite'
        frozen = snapshot_copy(registry, frozen_path)
        if any(frozen[k] != trusted[k] for k in ('nodes', 'events')):
            raise PinnedError('REGISTRY DIFFERS FROM EXTERNALLY PINNED CHECKPOINT')

        checked = [observations.verify_receipt(challenge, r, frozen_path, now)
                   for r in receipts]
        comparison = (observations.compare_verified(*checked)
                      if len(checked) == 2 else None)

        # Recheck the source before consuming proofs; the frozen backup is the
        # cryptographic source for all signatures, not the mutable live file.
        current = checkpoints.snapshot(registry)
        if any(current[k] != trusted[k] for k in ('nodes', 'events')):
            raise PinnedError('LIVE REGISTRY CHANGED SINCE PINNING')
        observations.record_once(replay_db, checked)

    return {
        'result': 'PINNED_SIGNED_OBSERVATIONS_VALID',
        'checkpoint_sha256': expected_sha256,
        'node_ids': [r['node_id'] for r in checked],
        'comparison': comparison,
        'chain_consensus_validated': False,
        'operator_independence_proven': False,
        'research_only': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('challenge', 'receipt', 'registry', 'seal', 'expected-sha256', 'replay-db'):
        parser.add_argument('--' + flag, required=True)
    parser.add_argument('--receipt-b', help='Second v0.5 receipt for comparison')
    args = parser.parse_args()
    try:
        receipts = [observations.read(args.receipt)]
        if args.receipt_b:
            receipts.append(observations.read(args.receipt_b))
        result = verify_pinned(observations.read(args.challenge), receipts,
                               args.registry, args.seal, args.expected_sha256,
                               args.replay_db)
        print(json.dumps(result, indent=2, sort_keys=True))
    except (PinnedError, checkpoints.CheckpointError, observations.ChallengeError,
            identities.IdentityError, sqlite3.Error, OSError, ValueError,
            TypeError, KeyError, IndexError) as exc:
        parser.exit(2, 'FAIL-CLOSED: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
