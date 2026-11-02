"""
Adversarial tests for AUNEYA/WVP v1.13.

Uses real Ed25519 keys and genuine
v1.11/v1.12 signed evidence fixtures.

No physical-device independence is claimed.
"""

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / 'tools' / 'auneya')
)

sys.path.insert(
    0,
    str(ROOT / 'tests')
)

import auneya_gate3_receipt_v113 as ack
import auneya_peer_gate_v16 as gate

from test_auneya_capsule_v112 import (
    PortableCapsuleTests
)


KEYGEN = '''
const k = require('node:crypto')
    .generateKeyPairSync('ed25519');

console.log(JSON.stringify({
    private: k.privateKey.export({
        format: 'pem',
        type: 'pkcs8'
    }),
    public: k.publicKey.export({
        format: 'pem',
        type: 'spki'
    })
}));
'''


class Gate3AcceptanceTests(unittest.TestCase):

    def setUp(self):

        fx = PortableCapsuleTests(
            'test_round_trip_and_highwater_idempotency'
        )

        fx.setUp()

        self.addCleanup(
            fx.doCleanups
        )

        self.fx = fx

        self.path = (
            fx.root / 'g3-ack.json'
        )

        keys = json.loads(
            subprocess.check_output(
                [
                    'node',
                    '-e',
                    KEYGEN
                ]
            )
        )

        self.private = (
            fx.root / 'recipient-private.pem'
        )

        self.public = (
            fx.root / 'recipient-public.pem'
        )

        self.private.write_text(
            keys['private']
        )

        self.public.write_text(
            keys['public']
        )

        self.private.chmod(0o600)
        self.public.chmod(0o600)

        self.pin = gate.sha(
            self.public.read_bytes()
        )

    def issue(self, output=None, pin=None):

        return ack.issue(
            self.fx.fx.trust,
            self.fx.path,
            self.fx.floor,
            self.private,
            self.public,
            pin or self.pin,
            output or self.path
        )

    def test_signed_acceptance_and_verification(self):

        result = self.issue()

        other = ack.verify(
            self.path,
            self.public,
            self.pin,
            self.fx.path,
            self.fx.floor
        )

        self.assertEqual(
            other['ack_sha256'],
            result['ack_sha256']
        )

        self.assertEqual(
            result['floor_status'],
            'initialized'
        )

        self.assertFalse(
            result['independent_devices_proven']
        )

        self.assertFalse(
            result['economic_activation']
        )

    def test_signature_tampering_fails_closed(self):

        self.issue()

        x = json.loads(
            self.path.read_text()
        )

        x['body']['sequence'] += 1

        self.path.write_bytes(
            gate.canonical(x) + b'\n'
        )

        with self.assertRaises(ValueError):

            ack.verify(
                self.path,
                self.public,
                self.pin
            )

    def test_wrong_pin_and_capsule_mismatch_fail(self):

        with self.assertRaises(ValueError):

            self.issue(
                pin='f' * 64
            )

        self.assertFalse(
            self.fx.floor.exists()
        )

        self.issue()

        other = (
            self.fx.root / 'unrelated.json'
        )

        other.write_bytes(
            b'not a capsule\n'
        )

        with self.assertRaisesRegex(
            ValueError,
            'Different evidence'
        ):

            ack.verify(
                self.path,
                self.public,
                self.pin,
                other
            )

    def test_preexisting_output_cannot_advance_floor(self):

        self.path.write_text(
            'reserved\n'
        )

        with self.assertRaisesRegex(
            ValueError,
            'exists'
        ):

            self.issue()

        self.assertFalse(
            self.fx.floor.exists()
        )

    def test_replay_idempotency(self):

        self.issue()

        duplicate = (
            self.fx.root / 'ack-again.json'
        )

        result = self.issue(
            output=duplicate
        )

        self.assertEqual(
            result['floor_status'],
            'unchanged'
        )

        checked = ack.verify(
            duplicate,
            self.public,
            self.pin,
            self.fx.path,
            self.fx.floor
        )

        self.assertEqual(
            checked['floor_status'],
            'unchanged'
        )

    def test_no_private_key_in_signed_receipt(self):

        self.issue()

        raw = self.path.read_bytes()

        self.assertNotIn(
            b'PRIVATE KEY',
            raw
        )

        self.assertNotIn(
            str(self.fx.root).encode(),
            raw
        )


if __name__ == '__main__':
    unittest.main()
