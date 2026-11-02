#!/usr/bin/env python3

"""
AUNEYA/WVP v1.13

Recipient-signed Gate 3 acceptance evidence.

Research implementation only.

A signed ACK proves that a pinned recipient key
signed a specific local verification result.

It does not prove:
- Independent physical devices
- Independent operators
- Truth of the observation
- External retention
- Global consensus
- Mainnet readiness
- Economic activation
"""

import argparse
import hashlib
import os
from pathlib import Path
import sys

import auneya_anchor_v19 as anchor
import auneya_capsule_v112 as capsule
import auneya_peer_gate_v16 as gate


FORMAT = 'auneya-gate3-recipient-ack-v1.13'

DOMAIN = (
    b'AUNEYA/WVP:GATE3-RECIPIENT-ACK:V1.13\x00'
)

MAX = 16 * 1024

FIELDS = {
    'format',
    'chain_id',
    'sequence',
    'anchor_sha256',
    'capsule_sha256',
    'trust_sha256',
    'floor_sha256',
    'recipient_pin',
    'floor_status',
    'non_value_research_only',
    'independent_devices_proven',
    'external_retention_proven',
    'economic_activation'
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, limit=MAX):

    raw = capsule.public_read(path, limit)
    obj = capsule.strict_bytes(raw)

    require(
        type(obj) is dict,
        'Invalid canonical JSON object'
    )

    return obj, raw


def floor_commitment(path, result):

    floor, raw = read(path, 4096)

    require(
        floor.get('format') == capsule.FLOOR
        and floor.get('chain_id')
            == result['chain_id']
        and floor.get('sequence')
            == result['sequence']
        and floor.get('anchor_sha256')
            == result['anchor_sha256']
        and floor.get('trust_sha256')
            == result['trust_sha256']
        and floor.get('last_capsule_sha256')
            == result['capsule_sha256'],
        'Recipient high-water does not match accepted capsule'
    )

    return digest(raw)


def issue(
    trust,
    evidence,
    floor,
    private_key,
    public_key,
    pin,
    output
):

    dest = Path(output)

    require(
        not dest.exists()
        and not dest.is_symlink(),
        'Receipt output exists'
    )

    require(
        dest.parent.is_dir()
        and not dest.parent.is_symlink()
        and dest.parent.stat().st_mode & 0o077 == 0,
        'Receipt directory must be private (0700)'
    )

    before_trust = digest(
        gate.read_private(trust, 32768)
    )

    pub = anchor.check_pin(
        public_key,
        pin
    )

    priv = anchor.private_file(
        private_key,
        MAX
    )

    probe = (
        DOMAIN
        + b'private-public-pair-check'
    )

    signature = anchor.crypto(
        'sign',
        priv,
        probe
    )

    require(
        anchor.crypto(
            'verify',
            pub,
            probe,
            signature
        ) == 'VERIFIED',
        'Recipient private/public key mismatch'
    )

    # Existing v1.12 verification performs:
    #
    # - Signed quorum verification
    # - Trust-pin verification
    # - Signed predecessor checks
    # - Monotonic floor validation
    # - Atomic high-water update
    #
    # Failure must never produce a signed ACK.

    result = capsule.verify_capsule(
        trust,
        evidence,
        floor
    )

    require(
        result['floor_status'] in (
            'initialized',
            'advanced',
            'unchanged'
        ),
        'Recipient high-water was not stored'
    )

    after_trust = digest(
        gate.read_private(trust, 32768)
    )

    require(
        before_trust == after_trust,
        'Recipient trust policy changed'
    )

    body = {
        'format': FORMAT,

        'chain_id':
            result['chain_id'],

        'sequence':
            result['sequence'],

        'anchor_sha256':
            result['anchor_sha256'],

        'capsule_sha256':
            result['capsule_sha256'],

        'trust_sha256':
            before_trust,

        'floor_sha256':
            None,

        'recipient_pin':
            pin,

        'floor_status':
            result['floor_status'],

        'non_value_research_only':
            True,

        'independent_devices_proven':
            False,

        'external_retention_proven':
            False,

        'economic_activation':
            False
    }

    body['floor_sha256'] = floor_commitment(
        floor,
        body
    )

    signed = anchor.crypto(
        'sign',
        priv,
        DOMAIN + gate.canonical(body)
    )

    record = {
        'body': body,
        'signature_b64': signed
    }

    raw = gate.canonical(record) + b'\n'

    require(
        len(raw) <= MAX,
        'ACK exceeds resource limit'
    )

    # Exclusive creation.
    # Private permissions.
    # File fsync.

    capsule.write_private(
        dest,
        raw
    )

    # Make directory entry durable where supported.

    dirfd = os.open(
        dest.parent,
        os.O_RDONLY
    )

    try:
        os.fsync(dirfd)

    finally:
        os.close(dirfd)

    return {
        'status':
            'SIGNED_RECIPIENT_RESEARCH_ACK',

        'ack_sha256':
            digest(raw),

        **body
    }


def verify(
    receipt,
    public_key,
    pin,
    evidence=None,
    floor=None
):

    obj, raw = read(receipt)

    require(
        set(obj) == {
            'body',
            'signature_b64'
        },
        'Unexpected ACK fields'
    )

    body = obj['body']

    require(
        type(body) is dict
        and set(body) == FIELDS,
        'Unexpected signed body fields'
    )

    require(
        body['format'] == FORMAT
        and body['non_value_research_only'] is True
        and body['independent_devices_proven'] is False
        and body['external_retention_proven'] is False
        and body['economic_activation'] is False,
        'Unsafe ACK claim'
    )

    require(
        type(body['sequence']) is int
        and 1 <= body['sequence'] <= gate.MAX_INT
        and type(body['chain_id']) is str
        and gate.CHAIN.fullmatch(
            body['chain_id']
        )
        and body['floor_status'] in (
            'initialized',
            'advanced',
            'unchanged'
        )
        and body['recipient_pin'] == pin,
        'Invalid ACK identity or sequence'
    )

    for name in (
        'anchor_sha256',
        'capsule_sha256',
        'trust_sha256',
        'floor_sha256',
        'recipient_pin'
    ):

        require(
            type(body[name]) is str
            and gate.HEX.fullmatch(
                body[name]
            ),
            'Invalid ACK digest: ' + name
        )

    pub = anchor.check_pin(
        public_key,
        pin
    )

    require(
        anchor.crypto(
            'verify',
            pub,
            DOMAIN + gate.canonical(body),
            obj['signature_b64']
        ) == 'VERIFIED',
        'Forged ACK'
    )

    if evidence is not None:

        require(
            digest(
                capsule.public_read(evidence)
            ) == body['capsule_sha256'],
            'Different evidence capsule'
        )

    if floor is not None:

        require(
            floor_commitment(
                floor,
                body
            ) == body['floor_sha256'],
            'Recipient high-water changed'
        )

    return {
        'status':
            'AUTHENTICATED_RECIPIENT_RESEARCH_ACK',

        'ack_sha256':
            digest(raw),

        **body
    }


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    subs = parser.add_subparsers(
        dest='action',
        required=True
    )

    a = subs.add_parser('issue')

    a.add_argument(
        '--trust',
        required=True
    )

    a.add_argument(
        '--capsule',
        required=True
    )

    a.add_argument(
        '--floor',
        required=True
    )

    a.add_argument(
        '--recipient-private',
        required=True
    )

    a.add_argument(
        '--recipient-public',
        required=True
    )

    a.add_argument(
        '--pin',
        required=True
    )

    a.add_argument(
        '--output',
        required=True
    )

    v = subs.add_parser('verify')

    v.add_argument(
        '--receipt',
        required=True
    )

    v.add_argument(
        '--recipient-public',
        required=True
    )

    v.add_argument(
        '--pin',
        required=True
    )

    v.add_argument('--capsule')
    v.add_argument('--floor')

    args = parser.parse_args()

    try:

        if args.action == 'issue':

            out = issue(
                args.trust,
                args.capsule,
                args.floor,
                args.recipient_private,
                args.recipient_public,
                args.pin,
                args.output
            )

        else:

            out = verify(
                args.receipt,
                args.recipient_public,
                args.pin,
                args.capsule,
                args.floor
            )

        sys.stdout.buffer.write(
            gate.canonical(out) + b'\n'
        )

    except (ValueError, OSError) as exc:

        parser.exit(
            2,
            'REJECTED: ' + str(exc) + '\n'
        )


if __name__ == '__main__':
    main()
