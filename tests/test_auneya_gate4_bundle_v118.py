"""Cryptographic positive path + fail-closed bundle contract adversaries."""

import hashlib
import json
import subprocess
import sys
import unittest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / 'tests'),
    str(ROOT / 'tools/auneya')
]

import auneya_capsule_v112 as cap
import auneya_gate4_bundle_v118 as gate
import test_auneya_quorum_v111 as fixture


class Gate4Tests(unittest.TestCase):

    def setUp(self):

        f = fixture.MultiKeeperTests(
            'test_authenticated_quorum_and_determinism'
        )

        f.setUp()

        self.addCleanup(f.doCleanups)

        self.f = f

        self.capsule = (
            f.root / 'v118-capsule.json'
        )

        cap.export_capsule(
            f.trust,
            f.b1,
            self.capsule
        )

        self.expected = hashlib.sha256(
            self.capsule.read_bytes()
        ).hexdigest()


    def invoke(
        self,
        command,
        extra=(),
        digest=None
    ):

        argv = [
            sys.executable,
            str(
                ROOT /
                'tools/auneya/auneya_gate4_bundle_v118.py'
            ),
            command,
            '--trust',
            str(self.f.trust),
            '--capsule',
            str(self.capsule),
            '--expected',
            digest or self.expected,
            *extra
        ]

        return subprocess.run(
            argv,
            capture_output=True,
            timeout=120
        )


    def test_deterministic_and_crypto_verified(self):

        x = self.invoke('create')
        y = self.invoke('create')

        self.assertEqual(
            x.returncode,
            0,
            x.stderr.decode()
        )

        self.assertEqual(
            x.stdout,
            y.stdout
        )

        data = gate.decode(
            x.stdout,
            65536
        )

        self.assertIs(
            data['dual']['python_verified'],
            True
        )

        self.assertIs(
            data['dual']['node_verified'],
            True
        )

        self.assertIs(
            data['independent_devices_proven'],
            False
        )

        self.assertEqual(
            data['capsule_sha256'],
            self.expected
        )

        self.assertEqual(
            data['dual_sha256'],
            gate.HEX(
                gate.json_canonical(data['dual'])
            )
        )


    def test_verified_roundtrip_and_exclusive_private_file(self):

        output = (
            self.f.root / 'v118-evidence.json'
        )

        a = self.invoke(
            'create',
            ('--output', str(output))
        )

        self.assertEqual(
            a.returncode,
            0,
            a.stderr.decode()
        )

        self.assertEqual(
            output.read_bytes(),
            a.stdout
        )

        self.assertEqual(
            output.stat().st_mode & 0o777,
            0o600
        )

        b = self.invoke(
            'verify',
            ('--input', str(output))
        )

        self.assertEqual(
            b.returncode,
            0,
            b.stderr.decode()
        )

        self.assertIn(
            b'PASS:',
            b.stdout
        )

        self.assertNotEqual(
            self.invoke(
                'create',
                ('--output', str(output))
            ).returncode,
            0
        )


    def test_modified_capsule_hash_is_rejected(self):

        self.assertNotEqual(
            self.invoke(
                'create',
                digest='0' * 64
            ).returncode,
            0
        )


    def test_tampered_claim_is_rejected(self):

        output = self.f.root / 'fake.json'

        report = gate.build(
            str(self.f.trust),
            str(self.capsule),
            self.expected
        )

        report['independent_devices_proven'] = True

        output.write_bytes(
            gate.json_canonical(report)
        )

        self.assertNotEqual(
            self.invoke(
                'verify',
                ('--input', str(output))
            ).returncode,
            0
        )


    def test_duplicate_key_is_rejected(self):

        x = self.invoke('create')

        self.assertEqual(
            x.returncode,
            0,
            x.stderr.decode()
        )

        altered = (
            x.stdout[:-2]
            + b',"format":"forged"}\n'
        )

        with self.assertRaisesRegex(
            ValueError,
            'duplicate JSON member'
        ):

            gate.decode(
                altered,
                65536
            )


    def test_symlink_report_rejected(self):

        original = (
            self.f.root / 'original.json'
        )

        original.write_bytes(
            self.invoke('create').stdout
        )

        alias = (
            self.f.root / 'alias.json'
        )

        alias.symlink_to(original)

        self.assertNotEqual(
            self.invoke(
                'verify',
                ('--input', str(alias))
            ).returncode,
            0
        )


    def test_canonical_and_resource_boundaries(self):

        for raw in (
            b'{}\n\n',
            b'{"a":1, "b":2}\n',
            b'{}',
            b' ' * 65537
        ):

            with self.subTest(
                raw=raw[:15]
            ), self.assertRaises(ValueError):

                gate.decode(
                    raw,
                    65536
                )

        schema = json.loads(
            (
                ROOT /
                'schemas/auneya-gate4-evidence-v1.18.schema.json'
            ).read_text()
        )

        self.assertEqual(
            set(schema['required']),
            set(schema['properties'])
        )

        self.assertFalse(
            schema['additionalProperties']
        )


if __name__ == '__main__':
    unittest.main()
