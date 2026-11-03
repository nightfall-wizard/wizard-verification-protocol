#!/usr/bin/env python3
"""AUNEYA/WVP v1.14: read-only offline audit of signed recipient history.

Verifies the FULL signed v1.12 quorum evidence for every entry again,
then separately verifies each v1.13 recipient signature. The head ACK hash
MUST be supplied from an independently retained trust domain.
No physical-device independence, global freshness, audit, mainnet or value claim.
"""

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import sys

import auneya_capsule_v112 as capsule
import auneya_gate3_receipt_v113 as recipient
import auneya_peer_gate_v16 as gate

FORMAT = 'auneya-gate3-audit-manifest-v1.14'
VERDICT = 'wvp-auneya-gate3-offline-audit-v1.14'
MAX_MANIFEST = 64 * 1024
MAX_ENTRIES = 64
FILENAME = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}\.json\Z')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def private_output(path):
    p = Path(path)
    need(
        not p.exists() and not p.is_symlink(),
        'Output already exists'
    )
    need(
        p.parent.is_dir() and not p.parent.is_symlink(),
        'Output parent must be a real directory'
    )
    need(
        stat.S_IMODE(p.parent.stat().st_mode) & 0o077 == 0,
        'Output parent must have mode 0700'
    )
    return p


def exact_name(name):
    need(
        type(name) is str
        and FILENAME.fullmatch(name) is not None
        and '..' not in name,
        'Unsafe manifest filename'
    )
    return name


def inspect(
    trust,
    manifest,
    recipient_public,
    recipient_pin,
    expected_head,
    floor=None,
    output=None
):
    """No state mutation unless optional exclusive report is requested."""

    need(
        type(expected_head) is str
        and gate.HEX.fullmatch(expected_head),
        'Expected head SHA256 must be a separately retained lowercase pin'
    )

    need(
        type(recipient_pin) is str
        and gate.HEX.fullmatch(recipient_pin),
        'Invalid independently pinned recipient key'
    )

    dest = private_output(output) if output is not None else None

    rootfile = Path(manifest).absolute()

    need(
        rootfile.parent.is_dir()
        and not rootfile.parent.is_symlink(),
        'Manifest directory cannot be a symlink'
    )

    raw = capsule.public_read(rootfile, MAX_MANIFEST)
    obj = capsule.strict_bytes(raw)

    need(
        set(obj) == {'format', 'entries'}
        and obj['format'] == FORMAT,
        'Invalid audit manifest'
    )

    entries = obj['entries']

    need(
        type(entries) is list
        and 1 <= len(entries) <= MAX_ENTRIES,
        'Invalid or excessive audit history'
    )

    initial_trust = gate.read_private(trust, 32768)
    trust_sha = sha(initial_trust)

    previous = None
    seen_capsules = set()
    seen_receipts = set()
    items = []

    for index, item in enumerate(entries):

        need(
            type(item) is dict
            and set(item) == {'capsule', 'ack'},
            'Incorrect manifest entry keys'
        )

        cpath = rootfile.parent / exact_name(item['capsule'])
        apath = rootfile.parent / exact_name(item['ack'])

        # Existing v1.12 verifier checks:
        # - Anchor signatures
        # - Keeper signatures
        # - Quorum threshold
        # - Signed predecessor
        # - WVP evidence commitment

        proof = capsule.verify_capsule(trust, cpath)

        # Existing v1.13 verifier checks:
        # - Recipient Ed25519 signature
        # - Independently pinned public key
        # - Signed acceptance commitments

        receipt = recipient.verify(
            apath,
            recipient_public,
            recipient_pin,
            cpath,
            floor if index == len(entries) - 1 else None
        )

        need(
            all(
                receipt[k] == proof[k]
                for k in (
                    'chain_id',
                    'sequence',
                    'anchor_sha256',
                    'capsule_sha256'
                )
            ),
            'Recipient ACK disagrees with independently checked quorum'
        )

        need(
            receipt['trust_sha256'] == trust_sha,
            'Recipient ACK was admitted under a different trust policy'
        )

        need(
            proof['signatures_verified'] is True,
            'Quorum signatures not authenticated'
        )

        need(
            proof['keeper_count'] >= proof['required_quorum'],
            'Keeper quorum insufficient'
        )

        need(
            proof['capsule_sha256'] not in seen_capsules
            and receipt['ack_sha256'] not in seen_receipts,
            'Duplicate or replayed audit record'
        )

        seen_capsules.add(proof['capsule_sha256'])
        seen_receipts.add(receipt['ack_sha256'])

        current_obj = capsule.strict_bytes(
            capsule.public_read(cpath)
        )

        if previous is None:

            need(
                receipt['sequence'] == 1
                and receipt['floor_status'] == 'initialized'
                and current_obj['previous'] is None,
                'History must start at admitted genesis sequence 1'
            )

        else:

            need(
                receipt['chain_id'] == previous['chain_id']
                and receipt['sequence'] == previous['sequence'] + 1
                and receipt['floor_status'] == 'advanced',
                'Skipped, stale, or unrelated recipient acceptance'
            )

            prior_bundle = current_obj['previous']

            need(
                type(prior_bundle) is dict
                and type(prior_bundle.get('anchor_b64')) is str,
                'Signed predecessor bundle missing'
            )

            previous_anchor = capsule.decoded(
                prior_bundle['anchor_b64'],
                1024 * 1024
            )

            need(
                sha(previous_anchor) == previous['anchor_sha256'],
                'Audit chain not bound to actual preceding anchor'
            )

        previous = receipt

        items.append({
            'sequence': receipt['sequence'],
            'anchor_sha256': receipt['anchor_sha256'],
            'capsule_sha256': receipt['capsule_sha256'],
            'ack_sha256': receipt['ack_sha256']
        })

    need(
        previous['ack_sha256'] == expected_head,
        'External receipt head mismatch: possible rollback or truncation'
    )

    need(
        gate.read_private(trust, 32768) == initial_trust,
        'Trust policy changed during audit'
    )

    result = {
        'format': VERDICT,
        'status': 'AUTHENTICATED_OFFLINE_RECIPIENT_HISTORY_RESEARCH',
        'chain_id': previous['chain_id'],
        'entry_count': len(items),
        'recipient_pin': recipient_pin,
        'trust_sha256': trust_sha,
        'manifest_sha256': sha(raw),
        'head_ack_sha256': expected_head,
        'head_anchor_sha256': previous['anchor_sha256'],
        'verified_entries': items,
        'signatures_verified': True,
        'independent_devices_proven': False,
        'external_retention_proven': False,
        'global_latest_proven': False,
        'independent_audit_completed': False,
        'mainnet_active': False,
        'economic_activation': False,
        'non_value_research_only': True
    }

    if dest is not None:

        capsule.write_private(
            dest,
            gate.canonical(result) + b'\n'
        )

        fd = os.open(dest.parent, os.O_RDONLY)

        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    return result


def main():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--trust', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--recipient-public', required=True)
    parser.add_argument('--recipient-pin', required=True)
    parser.add_argument('--expected-head', required=True)

    parser.add_argument(
        '--floor',
        help='Optional matching final floor snapshot'
    )

    parser.add_argument(
        '--output',
        help='Optional new private report (no overwrite)'
    )

    args = parser.parse_args()

    try:

        verdict = inspect(
            args.trust,
            args.manifest,
            args.recipient_public,
            args.recipient_pin,
            args.expected_head,
            args.floor,
            args.output
        )

        sys.stdout.buffer.write(
            gate.canonical(verdict) + b'\n'
        )

    except (OSError, ValueError, TypeError, KeyError) as exc:

        parser.exit(
            2,
            'REJECTED: ' + str(exc) + '\n'
        )


if __name__ == '__main__':
    main()
