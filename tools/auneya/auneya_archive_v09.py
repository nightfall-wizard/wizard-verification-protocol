#!/usr/bin/env python3

"""
WVP/AUNEYA v0.9:
Offline archival recheck of signed operator claims.

This is NOT a historical freshness,
independent-operator or consensus proof.
"""

import argparse
import hashlib
import json
import sqlite3
import tempfile

from contextlib import closing
from pathlib import Path
from urllib.parse import quote

import auneya_nightfall_challenge_v05 as v5
import auneya_pinned_observation_v07 as v7
import auneya_registry_checkpoint_v06 as v6
import auneya_wvp_evidence_batch_v08 as v8

F = 'auneya-archived-operator-claims-v0.9'

H = lambda b: hashlib.sha256(b).hexdigest()


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def key_snapshot(registry, seal, pin):

    locked = v6.read_seal(seal, pin)

    with tempfile.TemporaryDirectory() as d:

        local = Path(d) / 'registry.sqlite'

        snap = v7.snapshot_copy(
            registry,
            local,
        )

        ensure(
            all(
                snap[x] == locked[x]
                for x in ('nodes', 'events')
            ),
            'registry pin mismatch',
        )

        url = (
            'file:'
            + quote(str(local), safe='/')
            + '?mode=ro'
        )

        with closing(
            sqlite3.connect(url, uri=True)
        ) as db:

            rows = db.execute(
                'SELECT node_id,public_der FROM nodes'
            ).fetchall()

        keys = {
            name: key.hex()
            for name, key in rows
        }

    live = v6.snapshot(registry)

    ensure(
        all(
            live[x] == locked[x]
            for x in ('nodes', 'events')
        ),
        'registry changed',
    )

    return locked, keys


def expected_report(challenge, receipts, pin):

    commitment = {
        'checkpoint_sha256': pin,
        'challenge_sha256': H(
            v5.canonical(challenge)
        ),
        'receipt_sha256': sorted(
            H(v5.canonical(r))
            for r in receipts
        ),
    }

    report = v8.summarize(receipts)

    report.update(
        format='auneya-wvp-evidence-batch-v0.8',
        result='PINNED_OPERATOR_SIGNATURES_VALID',
        commitment=commitment,
        evidence_sha256=H(
            v5.canonical(commitment)
        ),
        wvp_proven=(
            'authenticated_pinned_public_'
            'operator_claims_only'
        ),
        consensus_validated=False,
        sybil_resistance_proven=False,
        independent_devices_proven=False,
        mainnet_mutated=False,
        non_value_research_only=True,
    )

    return report


def inspect(obj, pin):

    ensure(
        isinstance(obj, dict)
        and set(obj) == {
            'format',
            'seal',
            'challenge',
            'receipts',
            'keys',
            'report',
        },
        'capsule shape',
    )

    ensure(
        obj['format'] == F,
        'capsule version',
    )

    ensure(
        isinstance(pin, str)
        and len(pin) == 64
        and all(
            x in '0123456789abcdef'
            for x in pin
        ),
        'invalid external pin',
    )

    seal = obj['seal']

    ensure(
        isinstance(seal, dict)
        and H(v6.canonical(seal)) == pin,
        'external checkpoint mismatch',
    )

    v6.validate_snapshot(seal)

    known = {
        n['id']: n
        for n in seal['nodes']
    }

    receipts = obj['receipts']
    keys = obj['keys']
    challenge = obj['challenge']

    ensure(
        isinstance(receipts, list)
        and 2 <= len(receipts) <= 16,
        'receipt count',
    )

    ensure(
        isinstance(keys, dict),
        'key table',
    )

    names = []
    fingerprints = []

    for r in receipts:

        ensure(
            isinstance(r, dict)
            and set(r) == {
                'protocol',
                'kind',
                'challenge',
                'node_id',
                'observed_at',
                'status',
                'signature_hex',
            },
            'receipt fields',
        )

        name = r['node_id']
        when = r['observed_at']

        ensure(
            isinstance(name, str)
            and type(when) is int,
            'signed identity/time',
        )

        ensure(
            r['protocol'] == v5.VERSION
            and r['kind'] == 'attestation'
            and r['challenge'] == challenge,
            'wrong challenge',
        )

        # This checks the signed claimed time.
        # It does NOT prove historical freshness.

        v5.check_challenge(challenge, when)

        ensure(
            v5.check_status(
                r['status'],
                challenge,
            ) == r['status'],
            'unexpected status',
        )

        ensure(
            name in known
            and known[name]['state'] == 'active',
            'untrusted key',
        )

        key_hex = keys.get(name)

        ensure(
            isinstance(key_hex, str)
            and len(key_hex) == 88,
            'missing Ed25519 public key',
        )

        raw = bytes.fromhex(key_hex)

        prefix = bytes.fromhex(
            '302a300506032b6570032100'
        )

        ensure(
            len(raw) == 44
            and raw.startswith(prefix),
            'Ed25519 DER shape',
        )

        fingerprint = H(raw)

        ensure(
            fingerprint
            == known[name]['fingerprint'],
            'key/checkpoint mismatch',
        )

        body = {
            key: value
            for key, value in r.items()
            if key != 'signature_hex'
        }

        ensure(
            v5.valid_sig(
                raw,
                body,
                r['signature_hex'],
            ),
            'invalid signature',
        )

        names.append(name)
        fingerprints.append(fingerprint)

    ensure(
        names == sorted(set(names))
        and len(set(fingerprints))
        == len(fingerprints)
        and set(keys) == set(names),
        'nonunique signer/key',
    )

    report = expected_report(
        challenge,
        receipts,
        pin,
    )

    ensure(
        obj['report'] == report,
        'report integrity mismatch',
    )

    return {
        'result':
            'OFFLINE_SIGNED_STATEMENTS_AUTHENTIC',
        'evidence_sha256':
            report['evidence_sha256'],
        'historical_freshness_proven': False,
        'independent_operators_proven': False,
        'consensus_validated': False,
        'non_value_research_only': True,
    }


def capture(
    challenge,
    receipts,
    registry,
    seal,
    pin,
    ledger,
    now=None,
):

    ensure(
        2 <= len(receipts) <= 16,
        '2..16 receipts required',
    )

    locked, keys = key_snapshot(
        registry,
        seal,
        pin,
    )

    report = v8.verify_batch(
        challenge,
        receipts,
        registry,
        seal,
        pin,
        ledger,
        now,
    )

    obj = {
        'format': F,
        'seal': locked,
        'challenge': challenge,
        'receipts': sorted(
            receipts,
            key=lambda x: x['node_id'],
        ),
        'keys': {
            x['node_id']: keys[x['node_id']]
            for x in receipts
        },
        'report': report,
    }

    inspect(obj, pin)

    return obj


def main():

    p = argparse.ArgumentParser()

    sub = p.add_subparsers(
        dest='action',
        required=True,
    )

    a = sub.add_parser('capture')

    for flag in (
        'challenge',
        'registry',
        'seal',
        'pin',
        'ledger',
        'out',
    ):
        a.add_argument(
            '--' + flag,
            required=True,
        )

    a.add_argument(
        '--receipt',
        action='append',
        required=True,
    )

    b = sub.add_parser('inspect')

    b.add_argument(
        '--capsule',
        required=True,
    )

    b.add_argument(
        '--pin',
        required=True,
    )

    x = p.parse_args()

    try:

        if x.action == 'capture':

            out = Path(x.out)

            ensure(
                not out.exists()
                and not out.is_symlink(),
                'output exists',
            )

            v7.ensure_not_input(
                out,
                x.registry,
                x.seal,
            )

            ensure(
                out.absolute()
                != Path(x.ledger).absolute(),
                'output aliases replay ledger',
            )

            c = capture(
                v5.read(x.challenge),
                [
                    v5.read(f)
                    for f in x.receipt
                ],
                x.registry,
                x.seal,
                x.pin,
                x.ledger,
            )

            payload = v6.canonical(c)

            ensure(
                len(payload) < 3 * 1024 * 1024,
                'capsule oversized',
            )

            with out.open('xb') as f:
                f.write(payload)
                f.flush()

                import os
                os.fsync(f.fileno())

            out.chmod(0o600)

            print(
                json.dumps(inspect(c, x.pin))
            )

        else:

            file = v6.regular_private(
                x.capsule,
                3 * 1024 * 1024,
            )

            raw = file.read_bytes()

            c = json.loads(
                raw,
                object_pairs_hook=v5.pairs,
            )

            ensure(
                v6.canonical(c) == raw,
                'not canonical',
            )

            print(
                json.dumps(
                    inspect(c, x.pin),
                    sort_keys=True,
                )
            )

    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        sqlite3.Error,
    ) as e:

        p.exit(
            2,
            'FAIL-CLOSED: ' + str(e) + '\n',
        )


if __name__ == '__main__':
    main()
