#!/usr/bin/env python3
"""AUNEYA v1.21: deterministic dual-runtime cryptographic rejection.

Tests authentic signed capsule evidence against adversarial mutations.
No claim of independent physical devices, consensus or production.
"""

import argparse
import copy
import hashlib
import hmac
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import auneya_capsule_v112 as capsule
import auneya_dual_v117 as dual
import auneya_gate4_bundle_v118 as bundle
import auneya_gate4_adversarial_v119 as old_campaign
import auneya_wire_v120 as wire
import auneya_peer_gate_v16 as canon

FORMAT = 'auneya-gate4-differential-campaign-v1.21'
NODE = HERE / 'auneya_gate3_full_v116.js'
MAX_INPUT = 3 * 1024 * 1024
TIME_BUDGET = 600.0


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(obj):
    return canon.canonical(obj) + b'\n'


def mutants(original):
    parsed = capsule.strict_bytes(original)
    cases = []
    seen = {sha(original)}

    def add(name, data):
        digest = sha(data)
        need(digest not in seen, 'duplicate mutation: ' + name)
        seen.add(digest)
        cases.append((name, data))

    for name, data in old_campaign.adversaries(original):
        add('v119-' + name, data)

    def replace(name, key, value):
        obj = copy.deepcopy(parsed)
        obj[key] = value
        add(name, encoded(obj))

    for name, value in [
        ('null', None),
        ('false', False),
        ('negative', -1),
        ('zero', 0),
        ('string', '1'),
        ('string-two', '2'),
        ('float', 1.5),
        ('list', []),
        ('object', {}),
        ('max-overflow', 2**63),
        ('huge', 2**100),
    ]:
        replace('sequence-' + name, 'sequence', value)

    for name, value in [
        ('empty', ''),
        ('space', ' '),
        ('uppercase', 'AUNEYA'),
        ('slash', 'broken/chain'),
        ('newline', 'a\nb'),
        ('unicode', 'äuneya'),
        ('too-long', 'a' * 81),
        ('null', None),
    ]:
        replace('chain-' + name, 'chain_id', value)

    for key in ('anchor_sha256', 'quorum_report_sha256'):
        for name, value in [
            ('empty', ''),
            ('null', None),
            ('bool', False),
            ('number', 1),
            ('bad-hex', 'z' * 64),
            ('uppercase', 'F' * 64),
            ('short', '0' * 63),
            ('long', '0' * 65),
            ('zero', '0' * 64),
        ]:
            replace(key + '-' + name, key, value)

    for name, value in [
        ('null', None),
        ('false', False),
        ('array', []),
        ('empty', {}),
        ('string', 'invalid'),
        ('number', 2),
        ('receipts-only', {'receipts': []}),
    ]:
        replace('current-' + name, 'current', value)

    for name, value in [
        ('false', False),
        ('empty', {}),
        ('array', []),
        ('string', 'invalid'),
        ('number', 42),
    ]:
        replace('previous-' + name, 'previous', value)

    for number in range(8):
        obj = copy.deepcopy(parsed)
        obj['unexpected_extension_' + str(number)] = number
        add('unknown-field-' + str(number), encoded(obj))

    for name, data in [
        ('bom', b'\xef\xbb\xbf' + original),
        ('leading-space', b' ' + original),
        ('trailing-space', original + b' '),
        ('trailing-cr', original + b'\r'),
        ('crlf', original[:-1] + b'\r\n'),
        ('missing-lf', original[:-1]),
        ('trailing-nul', original + b'\0'),
        ('prefix-nul', b'\0' + original),
        ('first-colon-space', original.replace(b':', b': ', 1)),
        ('first-comma-space', original.replace(b',', b', ', 1)),
        ('upper-field', original.replace(b'"format"', b'"FORMAT"', 1)),
    ]:
        add('framing-' + name, data)

    def corrupt_base64(label, setter, count, getter):
        value = getter(parsed)
        need(
            isinstance(value, str) and len(value) >= count,
            'insufficient signed evidence: ' + label
        )
        for index in range(count):
            obj = copy.deepcopy(parsed)
            value = getter(obj)
            replacement = 'A' if value[index] != 'A' else 'B'
            changed = value[:index] + replacement + value[index + 1:]
            setter(obj, changed)
            add(label + '-byte-%02d' % index, encoded(obj))

    corrupt_base64(
        'signed-anchor',
        lambda obj, value: obj['current'].__setitem__('anchor_b64', value),
        24,
        lambda obj: obj['current']['anchor_b64']
    )

    corrupt_base64(
        'signed-keeper',
        lambda obj, value: obj['current']['receipts'][0].__setitem__(
            'payload_b64', value
        ),
        24,
        lambda obj: obj['current']['receipts'][0]['payload_b64']
    )

    need(len(cases) >= 100, 'adversarial corpus too small')
    return cases


def build(trust, candidate, expected):
    need(
        isinstance(expected, str) and bundle.SHA.fullmatch(expected),
        'independently supplied lowercase SHA-256 required'
    )

    raw, schema_sha = wire.profile(candidate)

    need(
        hmac.compare_digest(sha(raw), expected),
        'external digest mismatch'
    )

    trust_before = dual.read(trust, 32768, True)

    baseline = bundle.build(trust, candidate, expected)

    need(
        baseline['dual']['python_verified'] is True
        and baseline['dual']['node_verified'] is True,
        'clean baseline not independently verified'
    )

    attacks = mutants(raw)
    outcomes = []
    deadline = time.monotonic() + TIME_BUDGET

    with tempfile.TemporaryDirectory(prefix='auneya-v121-') as sandbox:
        for index, (name, changed) in enumerate(attacks):
            need(
                time.monotonic() < deadline,
                'campaign deadline exceeded'
            )

            path = Path(sandbox) / ('attack-%03d.json' % index)

            fd = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600
            )

            with os.fdopen(fd, 'wb') as output:
                output.write(changed)
                output.flush()
                os.fsync(output.fileno())

            try:
                capsule.verify_capsule(trust, path)
            except ValueError:
                python_reject = True
            else:
                python_reject = False

            timeout = max(
                0.1,
                min(12.0, deadline - time.monotonic())
            )

            result = subprocess.run(
                [
                    'node',
                    str(NODE),
                    '--trust',
                    str(trust),
                    '--capsule',
                    str(path),
                    '--expected-capsule',
                    sha(changed)
                ],
                capture_output=True,
                timeout=timeout
            )

            node_reject = (
                result.returncode == 2
                and result.stderr.startswith(b'REJECTED: ')
                and not result.stdout
            )

            need(
                python_reject and node_reject,
                'VERIFIER DIVERGENCE OR ACCEPTED ATTACK: ' + name
            )

            outcomes.append({
                'id': name,
                'sha256': sha(changed),
                'python_rejected': True,
                'node_rejected': True
            })

    need(
        dual.read(candidate, MAX_INPUT) == raw
        and dual.read(trust, 32768, True) == trust_before,
        'original input changed during campaign'
    )

    return {
        'format': FORMAT,
        'status': 'LOCAL_DUAL_RUNTIME_REJECTION_CONFIRMED',
        'capsule_sha256': expected,
        'trust_sha256': sha(trust_before),
        'wire_schema_sha256': schema_sha,
        'baseline_evidence_sha256': sha(bundle.json_canonical(baseline)),
        'cases_passed': len(outcomes),
        'cases': outcomes,
        'python_verified': True,
        'node_verified': True,
        'physical_device_independence_proven': False,
        'external_retention_proven': False,
        'independent_audit_completed': False,
        'public_network_active': False,
        'mainnet_active': False,
        'economic_activation': False,
        'non_value_research_only': True
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('create', 'verify'))
    parser.add_argument('--trust', required=True)
    parser.add_argument('--capsule', required=True)
    parser.add_argument('--expected', required=True)
    parser.add_argument('--output')
    parser.add_argument('--input')

    args = parser.parse_args()

    report = bundle.json_canonical(
        build(args.trust, args.capsule, args.expected)
    )

    if args.action == 'create':
        if args.output:
            bundle.secure_write(args.output, report)
        sys.stdout.buffer.write(report)
    else:
        need(args.input and not args.output, 'verify requires --input only')
        saved = bundle.secure_read(args.input, 131072)
        need(
            hmac.compare_digest(saved, report),
            'saved evidence differs'
        )
        print('PASS: deterministic v1.21 dual-runtime rejection contract')


if __name__ == '__main__':
    try:
        main()
    except (
        ValueError,
        OSError,
        RuntimeError,
        KeyError,
        TypeError,
        subprocess.SubprocessError
    ) as error:
        sys.exit('REJECTED: ' + str(error))
