"""
AUNEYA/WVP v1.15

Independent Python/Node.js conformance tests.
Uses real Ed25519 signatures.

No physical device independence claimed.
"""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
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

import auneya_gate3_receipt_v113 as receipts
import auneya_peer_gate_v16 as gate

import test_auneya_gate3_receipt_v113 as prior

NODE = (
    ROOT /
    'tools/auneya/auneya_gate3_interop_v115.js'
)

VECTORS = (
    ROOT /
    'tests/vectors/gate3-v115'
)


class RecipientInteropTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        fixture = prior.Gate3AcceptanceTests(
            'test_signed_acceptance_and_verification'
        )

        try:
            fixture.setUp()
            fixture.issue()

            cls._base_fixture = fixture
            cls._ack_bytes = fixture.path.read_bytes()

            cls._head = hashlib.sha256(
                cls._ack_bytes
            ).hexdigest()

        except BaseException:
            fixture.doCleanups()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            cls._base_fixture.doCleanups()
        finally:
            super().tearDownClass()

    def setUp(self):
        self.fixture = self._base_fixture

        self.fixture.path.write_bytes(
            self._ack_bytes
        )

        self.head = self._head

    def invoke(self, **overrides):
        args = {
            'receipt':
                self.fixture.path,

            'recipient-public':
                self.fixture.public,

            'pin':
                self.fixture.pin,

            'expected-head':
                self.head,

            'capsule':
                self.fixture.fx.path,

            'floor':
                self.fixture.fx.floor
        }

        args.update(overrides)

        command = [
            'node',
            str(NODE)
        ]

        for key, value in args.items():
            if value is not None:
                command.extend([
                    '--' + key,
                    str(value)
                ])

        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20
        )

    def assert_rejected(self, **kwargs):
        result = self.invoke(**kwargs)

        self.assertEqual(
            result.returncode,
            2,
            (result.stdout, result.stderr)
        )

        self.assertIn(
            'REJECTED:',
            result.stderr
        )

        self.assertNotIn(
            'AUTHENTICATED_RECIPIENT_RESEARCH_ACK',
            result.stdout
        )

    def rewrite(self, change):
        obj = json.loads(
            self.fixture.path.read_text()
        )

        change(obj)

        self.fixture.path.write_bytes(
            gate.canonical(obj) + b'\n'
        )

        return hashlib.sha256(
            self.fixture.path.read_bytes()
        ).hexdigest()

    def test_matches_python_v113(self):
        python_result = receipts.verify(
            self.fixture.path,
            self.fixture.public,
            self.fixture.pin,
            self.fixture.fx.path,
            self.fixture.fx.floor
        )

        result = self.invoke()

        self.assertEqual(
            result.returncode,
            0,
            result.stderr
        )

        node_result = json.loads(
            result.stdout
        )

        self.assertEqual(
            node_result['ack_sha256'],
            python_result['ack_sha256']
        )

        self.assertEqual(
            node_result['chain_id'],
            python_result['chain_id']
        )

        self.assertEqual(
            int(node_result['sequence_decimal']),
            python_result['sequence']
        )

        self.assertTrue(
            node_result['recipient_signature_verified']
        )

        self.assertFalse(
            node_result['quorum_independently_verified']
        )

        self.assertFalse(
            node_result['independent_devices_proven']
        )

    def test_rejects_external_head_rollback(self):
        wrong = (
            'f' * 64
            if self.head != 'f' * 64
            else 'e' * 64
        )

        self.assert_rejected(
            **{'expected-head': wrong}
        )

    def test_rejects_wrong_recipient_pin(self):
        wrong = (
            '0' * 64
            if self.fixture.pin != '0' * 64
            else '1' * 64
        )

        self.assert_rejected(
            pin=wrong
        )

    def test_rejects_signed_body_tampering(self):
        new_head = self.rewrite(
            lambda obj:
                obj['body'].__setitem__(
                    'chain_id',
                    'forged-chain'
                )
        )

        self.assert_rejected(
            **{'expected-head': new_head}
        )

    def test_rejects_signature_forgery(self):
        new_head = self.rewrite(
            lambda obj:
                obj.__setitem__(
                    'signature_b64',
                    'A' * 86 + '=='
                )
        )

        self.assert_rejected(
            **{'expected-head': new_head}
        )

    def test_rejects_unsafe_claims(self):
        new_head = self.rewrite(
            lambda obj:
                obj['body'].__setitem__(
                    'independent_devices_proven',
                    True
                )
        )

        self.assert_rejected(
            **{'expected-head': new_head}
        )

    def test_rejects_noncanonical_json(self):
        raw = self.fixture.path.read_bytes()

        obj = json.loads(raw)

        self.fixture.path.write_text(
            json.dumps(
                obj,
                indent=2
            ) + '\n'
        )

        head = hashlib.sha256(
            self.fixture.path.read_bytes()
        ).hexdigest()

        self.assert_rejected(
            **{'expected-head': head}
        )

    def test_rejects_duplicate_json_keys(self):
        raw = self.fixture.path.read_bytes()

        changed = raw.replace(
            b'"signature_b64":',
            b'"signature_b64":"fake","signature_b64":',
            1
        )

        self.fixture.path.write_bytes(
            changed
        )

        head = hashlib.sha256(
            changed
        ).hexdigest()

        self.assert_rejected(
            **{'expected-head': head}
        )

    def test_rejects_capsule_substitution(self):
        with tempfile.TemporaryDirectory(
            dir=self.fixture.path.parent
        ) as temporary:
            swapped = (
                Path(temporary) /
                'other.json'
            )

            swapped.write_bytes(
                b'not the signed capsule\n'
            )

            self.assert_rejected(
                capsule=swapped
            )

    def test_rejects_floor_substitution(self):
        with tempfile.TemporaryDirectory(
            dir=self.fixture.path.parent
        ) as temporary:
            swapped = (
                Path(temporary) /
                'other.json'
            )

            swapped.write_bytes(
                b'not the signed floor\n'
            )

            self.assert_rejected(
                floor=swapped
            )

    def test_rejects_symlink(self):
        link = (
            self.fixture.path.parent /
            'linked-ack.json'
        )

        link.symlink_to(
            self.fixture.path
        )

        self.assert_rejected(
            receipt=link
        )

    def test_rejects_bad_key_permissions(self):
        public = (
            self.fixture.path.parent /
            'unprotected-public.pem'
        )

        public.write_bytes(
            self.fixture.public.read_bytes()
        )

        public.chmod(0o644)

        self.assert_rejected(
            **{'recipient-public': public}
        )

    def test_rejects_oversized_ack(self):
        self.fixture.path.write_bytes(
            b'A' * 16385
        )

        head = hashlib.sha256(
            self.fixture.path.read_bytes()
        ).hexdigest()

        self.assert_rejected(
            **{'expected-head': head}
        )

    def test_fixed_vectors_python_node_large_integer(self):
        index = json.loads(
            (VECTORS / 'index.json').read_text()
        )

        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)

            folder.chmod(0o700)

            for name in (
                'receipt.json',
                'recipient-public.pem'
            ):
                shutil.copyfile(
                    VECTORS / name,
                    folder / name
                )

                (folder / name).chmod(
                    0o600
                )

            python_result = receipts.verify(
                folder / 'receipt.json',
                folder / 'recipient-public.pem',
                index['recipient_pin']
            )

            result = self.invoke(
                receipt=folder / 'receipt.json',

                **{
                    'recipient-public':
                        folder / 'recipient-public.pem',

                    'pin':
                        index['recipient_pin'],

                    'expected-head':
                        index['ack_sha256'],

                    'capsule': None,

                    'floor': None
                }
            )

            self.assertEqual(
                result.returncode,
                0,
                result.stderr
            )

            node_result = json.loads(
                result.stdout
            )

            self.assertEqual(
                int(node_result['sequence_decimal']),
                9007199254740993
            )

            self.assertEqual(
                int(node_result['sequence_decimal']),
                python_result['sequence']
            )

            self.assertEqual(
                python_result['ack_sha256'],
                index['ack_sha256']
            )

    def test_public_vectors_reproducible(self):
        with tempfile.TemporaryDirectory() as temporary:
            generated = (
                Path(temporary) /
                'vectors'
            )

            result = subprocess.run(
                [
                    'node',
                    str(NODE),
                    '--generate-vectors',
                    str(generated)
                ],
                capture_output=True,
                text=True,
                timeout=20
            )

            self.assertEqual(
                result.returncode,
                0,
                result.stderr
            )

            for name in (
                'receipt.json',
                'recipient-public.pem',
                'index.json'
            ):
                self.assertEqual(
                    (generated / name).read_bytes(),
                    (VECTORS / name).read_bytes()
                )


if __name__ == '__main__':
    unittest.main()
