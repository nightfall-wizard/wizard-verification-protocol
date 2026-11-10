#!/usr/bin/env python3
"""AUNEYA/WVP v1.19: offline, deterministic dual-runtime adversarial campaign.

Does not attest to device independence, third-party review, or production safety.
Each mutated capsule is rehashed to isolate semantic/cryptographic rejection
from the external-digest guard. No secret keys are handled by this program.
"""

import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import auneya_capsule_v112 as capsule
import auneya_dual_v117 as dual
import auneya_gate4_bundle_v118 as gate4
import auneya_peer_gate_v16 as canonical_lib

FORMAT = 'auneya-gate4-adversarial-campaign-v1.19'
NODE = HERE / 'auneya_gate3_full_v116.js'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def serialize(obj):
    return canonical_lib.canonical(obj) + b'\n'


def flip_hash(value):
    need(type(value) is str and len(value) == 64, 'invalid hash field')
    return ('0' if value[0] != '0' else '1') + value[1:]


def flip_signature(value):
    need(type(value) is str and len(value) >= 4, 'invalid signature')
    return ('A' if value[0] != 'A' else 'B') + value[1:]


def mutate_signed(encoded, member, transform):
    raw = base64.b64decode(encoded, validate=True)
    signed = capsule.strict_bytes(raw)
    need(type(signed) is dict and 'body' in signed, 'bad signed object')
    signed = copy.deepcopy(signed)
    if member == 'body':
        transform(signed['body'])
    else:
        transform(signed)
    return base64.b64encode(serialize(signed)).decode('ascii')


def adversaries(raw):
    """Fixed adversarial corpus, no randomness or dependency on wall time."""
    original = capsule.strict_bytes(raw)
    cases = []

    def add(name, update):
        obj = copy.deepcopy(original)
        update(obj)
        changed = serialize(obj)
        need(changed != raw, 'ineffective mutation: ' + name)
        cases.append((name, changed))

    add('wrong-format', lambda x: x.__setitem__('format', 'invalid-v119'))
    add('wrong-chain', lambda x: x.__setitem__(
        'chain_id', 'wrong-chain-v119' if x['chain_id'] != 'wrong-chain-v119' else 'other-chain-v119'
    ))
    add('sequence-tamper', lambda x: x.__setitem__(
        'sequence', x['sequence'] + 1 if x['sequence'] < 2**63 - 1 else x['sequence'] - 1
    ))
    add('anchor-commitment-tamper', lambda x: x.__setitem__(
        'anchor_sha256', flip_hash(x['anchor_sha256'])
    ))
    add('report-commitment-tamper', lambda x: x.__setitem__(
        'quorum_report_sha256', flip_hash(x['quorum_report_sha256'])
    ))
    add('missing-quorum', lambda x: x['current'].__setitem__('receipts', []))
    add('duplicate-keeper', lambda x: x['current'].__setitem__(
        'receipts', [copy.deepcopy(x['current']['receipts'][0])] * 2
    ))
    add('unknown-keeper-pin', lambda x: x['current']['receipts'][0].__setitem__(
        'pin', flip_hash(x['current']['receipts'][0]['pin'])
    ))

    def signed_anchor_body(x):
        x['current']['anchor_b64'] = mutate_signed(
            x['current']['anchor_b64'], 'body',
            lambda body: body.__setitem__('state_sha256', flip_hash(body['state_sha256']))
        )

    def signed_anchor_signature(x):
        x['current']['anchor_b64'] = mutate_signed(
            x['current']['anchor_b64'], 'signed',
            lambda obj: obj.__setitem__('signature_b64', flip_signature(obj['signature_b64']))
        )

    def signed_keeper_body(x):
        item = x['current']['receipts'][0]
        item['payload_b64'] = mutate_signed(
            item['payload_b64'], 'body',
            lambda body: body.__setitem__('anchor_sha256', flip_hash(body['anchor_sha256']))
        )

    def signed_keeper_signature(x):
        item = x['current']['receipts'][0]
        item['payload_b64'] = mutate_signed(
            item['payload_b64'], 'signed',
            lambda obj: obj.__setitem__('signature_b64', flip_signature(obj['signature_b64']))
        )

    add('forged-anchor-body', signed_anchor_body)
    add('forged-anchor-signature', signed_anchor_signature)
    add('forged-keeper-body', signed_keeper_body)
    add('forged-keeper-signature', signed_keeper_signature)

    cases.extend([
        ('duplicate-json-key', raw[:-2] + b',"format":"forged"}\n'),
        ('noncanonical-lf', raw + b'\n'),
        ('truncated-capsule', raw[:-7]),
    ])

    need(len({sha(item[1]) for item in cases}) == len(cases),
         'duplicate adversarial vectors')
    return cases


def run(trust, capsule_path, independently_expected):
    need(type(independently_expected) is str and gate4.SHA.fullmatch(independently_expected),
         'independent lowercase capsule SHA-256 required')

    # Baseline: run the existing full Python+Node verification and v1.18
    # schema-bound evidence contract before touching adversarial vectors.
    baseline = gate4.build(trust, capsule_path, independently_expected)
    raw = dual.read(capsule_path, 3 * 1024 * 1024)
    initial_trust = dual.read(trust, 32768, True)
    need(sha(raw) == independently_expected, 'source capsule changed')
    need(baseline['dual']['python_verified'] is True and
         baseline['dual']['node_verified'] is True, 'baseline mismatch')

    cases = adversaries(raw)
    results = []
    with tempfile.TemporaryDirectory(prefix='auneya-v119-') as sandbox:
        for number, (name, altered) in enumerate(cases):
            path = Path(sandbox) / ('case-%02d.json' % number)
            # Exclusive private file. Never overwrite any source evidence.
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(altered)
                stream.flush()
                os.fsync(stream.fileno())

            try:
                capsule.verify_capsule(trust, path)
            except ValueError:
                python_rejected = True
            else:
                python_rejected = False

            # Deliberately supply the attacker's updated digest. This tests
            # structural and signed-evidence defenses, NOT external freshness.
            executed = subprocess.run(
                ['node', str(NODE), '--trust', str(trust),
                 '--capsule', str(path), '--expected-capsule', sha(altered)],
                capture_output=True, timeout=60
            )
            node_rejected = (executed.returncode == 2 and
                             executed.stderr.startswith(b'REJECTED: ') and
                             len(executed.stdout) == 0)

            need(python_rejected and node_rejected,
                 'VERIFIER DISAGREEMENT OR ACCEPTED ATTACK: ' + name)
            results.append({
                'case': name,
                'mutant_sha256': sha(altered),
                'python_rejected': True,
                'node_rejected': True,
            })

    # Explicit time-of-check/time-of-use guard on original inputs.
    need(dual.read(capsule_path, 3 * 1024 * 1024) == raw and
         dual.read(trust, 32768, True) == initial_trust,
         'original input changed during campaign')

    return {
        'format': FORMAT,
        'status': 'LOCAL_ADVERSARIAL_CONFORMANCE_PASSED',
        'baseline_gate4_sha256': sha(gate4.json_canonical(baseline)),
        'capsule_sha256': independently_expected,
        'trust_sha256': sha(initial_trust),
        'cases_passed': len(results),
        'cases': results,
        'python_verified': True,
        'node_verified': True,
        'independent_devices_proven': False,
        'external_retention_proven': False,
        'independent_audit_completed': False,
        'mainnet_active': False,
        'economic_activation': False,
        'non_value_research_only': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trust', required=True)
    parser.add_argument('--capsule', required=True)
    parser.add_argument('--expected', required=True,
                        help='SHA-256 independently pinned outside the capsule')
    parser.add_argument('--output', help='new, private, mode-0600 report')
    args = parser.parse_args()
    report = run(args.trust, args.capsule, args.expected)
    output = gate4.json_canonical(report)
    if args.output:
        gate4.secure_write(args.output, output)
    sys.stdout.buffer.write(output)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError,
            KeyError, TypeError) as error:
        sys.exit('REJECTED: ' + str(error))
