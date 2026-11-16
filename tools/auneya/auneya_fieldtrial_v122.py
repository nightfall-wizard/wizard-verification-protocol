#!/usr/bin/env python3
"""AUNEYA/WVP v1.22 offline Gate-3 field-trial artifact verifier.

Verifies existing signed quorum and signed recipient ACK in Python and Node,
against out-of-band digests. Read-only: NEVER updates the recipient floor.
A successful local report is NOT physical-device independence evidence.
"""
import argparse
import hashlib
import hmac
import json
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import auneya_dual_v117 as dual
import auneya_gate3_receipt_v113 as ack
import auneya_gate4_bundle_v118 as bundle

FORMAT = 'auneya-gate3-fieldtrial-offline-v1.22'
SHA = re.compile(r'[0-9a-f]{64}\Z')
NODE_ACK = HERE / 'auneya_gate3_interop_v115.js'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def equal(a, b, message):
    require(isinstance(a, str) and isinstance(b, str) and
            hmac.compare_digest(a, b), message)


def expected(value, label):
    require(type(value) is str and SHA.fullmatch(value),
            'Independently pinned lowercase SHA-256 missing: ' + label)
    return value


def run(args):
    for field in ('expected_trust', 'expected_capsule',
                  'expected_ack', 'expected_floor', 'recipient_pin'):
        expected(getattr(args, field), field)

    # Bounded non-following readers; trust must be in a private directory.
    read_map = {
        'trust': (args.trust, 32768, True),
        'capsule': (args.capsule, 3 * 1024 * 1024, False),
        'ack': (args.ack, 16384, False),
        'floor': (args.floor, 4096, True),
        'recipient_public': (args.recipient_public, 16384, True),
    }
    before = {
        label: dual.read(path, limit, private)
        for label, (path, limit, private) in read_map.items()
    }
    for label in ('trust', 'capsule', 'ack', 'floor'):
        equal(digest(before[label]), getattr(args, 'expected_' + label),
              'External digest mismatch: ' + label)
    equal(digest(before['recipient_public']), args.recipient_pin,
          'Independent recipient public-key pin mismatch')

    # Existing full-quorum verification is independently implemented in Node.
    quorum = dual.run(SimpleNamespace(
        trust=str(args.trust), capsule=str(args.capsule),
        expected=args.expected_capsule))
    require(quorum['python_verified'] is True and
            quorum['node_verified'] is True,
            'Python/Node quorum verification failed')

    # Existing recipient ACK signature is independently checked in both runtimes.
    py = ack.verify(args.ack, args.recipient_public, args.recipient_pin,
                    args.capsule, args.floor)
    cmd = ['node', str(NODE_ACK), '--receipt', str(args.ack),
           '--recipient-public', str(args.recipient_public),
           '--pin', args.recipient_pin,
           '--expected-head', args.expected_ack,
           '--capsule', str(args.capsule), '--floor', str(args.floor)]
    node = subprocess.run(cmd, capture_output=True, timeout=45)
    require(node.returncode == 0 and 0 < len(node.stdout) <= 32768
            and not node.stderr, 'Node recipient ACK verification failed')
    try:
        js = json.loads(node.stdout)
    except (ValueError, UnicodeError) as exc:
        raise ValueError('Invalid Node verifier report') from exc
    require(type(js) is dict and
            js.get('external_head_matched') is True and
            js.get('recipient_signature_verified') is True and
            js.get('quorum_independently_verified') is False and
            js.get('independent_devices_proven') is False and
            js.get('external_retention_proven') is False and
            js.get('economic_activation') is False and
            js.get('non_value_research_only') is True,
            'Invalid Node ACK verdict or overstated claim')

    for name, a, b in (
        ('chain', quorum['chain_id'], py['chain_id']),
        ('chain Node', py['chain_id'], js['chain_id']),
        ('sequence', quorum['sequence'], str(py['sequence'])),
        ('sequence Node', str(py['sequence']), js['sequence_decimal']),
        ('capsule', quorum['capsule_sha256'], py['capsule_sha256']),
        ('capsule Node', py['capsule_sha256'], js['capsule_sha256']),
        ('anchor', quorum['anchor_sha256'], py['anchor_sha256']),
        ('trust', quorum['trust_sha256'], py['trust_sha256']),
        ('floor', args.expected_floor, py['floor_sha256']),
        ('recipient', args.recipient_pin, py['recipient_pin']),
        ('ACK', args.expected_ack, py['ack_sha256']),
        ('ACK Node', py['ack_sha256'], js['ack_sha256']),
    ):
        require(a == b, 'Cross-runtime or commitment disagreement: ' + name)

    require(py['non_value_research_only'] is True and
            py['independent_devices_proven'] is False and
            py['external_retention_proven'] is False and
            py['economic_activation'] is False,
            'Unsafe Python ACK verdict')
    require(py['floor_status'] in ('initialized', 'advanced', 'unchanged'),
            'Signed recipient floor missing')
    require(js['recipient_pin'] == args.recipient_pin,
            'Node recipient pin mismatch')

    # Never claim that software can infer two genuinely separate devices.
    for label, (path, limit, private) in read_map.items():
        require(dual.read(path, limit, private) == before[label],
                'Input changed during verification: ' + label)

    return {
        'format': FORMAT,
        'status': 'OFFLINE_ARTIFACTS_CRYPTOGRAPHICALLY_VERIFIED',
        'chain_id': quorum['chain_id'],
        'sequence_decimal': quorum['sequence'],
        'trust_sha256': args.expected_trust,
        'capsule_sha256': args.expected_capsule,
        'ack_sha256': args.expected_ack,
        'floor_sha256': args.expected_floor,
        'recipient_pin': args.recipient_pin,
        'anchor_sha256': quorum['anchor_sha256'],
        'quorum_report_sha256': quorum['quorum_report_sha256'],
        'keeper_count': quorum['keeper_count'],
        'required_quorum': quorum['required_quorum'],
        'floor_status': py['floor_status'],
        'python_quorum_verified': True,
        'node_quorum_verified': True,
        'python_ack_verified': True,
        'node_ack_verified': True,
        'inputs_unchanged': True,
        'independent_devices_proven': False,
        'external_retention_proven': False,
        'real_rollback_experiment_proven': False,
        'independent_audit_completed': False,
        'mainnet_active': False,
        'economic_activation': False,
        'non_value_research_only': True,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('trust', 'capsule', 'ack', 'floor', 'recipient-public',
                 'recipient-pin', 'expected-trust', 'expected-capsule',
                 'expected-ack', 'expected-floor'):
        ap.add_argument('--' + name, required=True)
    ap.add_argument('--report', help='New file in private 0700 directory')
    args = ap.parse_args()
    report = bundle.json_canonical(run(args))
    if args.report:
        bundle.secure_write(args.report, report)
    sys.stdout.buffer.write(report)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        sys.exit('REJECTED: ' + str(exc))
