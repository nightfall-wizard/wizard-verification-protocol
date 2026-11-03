"""
AUNEYA v1.16:
Genuine Python-signed evidence verified by Node.js.

Offline, non-value, adversarial interoperability.
No independent-device or production-audit claim.
"""

import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / 'tools' / 'auneya'),
    str(ROOT / 'tests')
]

import auneya_peer_gate_v16 as gate
import auneya_capsule_v112 as portable
import auneya_quorum_v111 as quorum
import test_auneya_quorum_v111 as base

NODE = (
    ROOT /
    'tools/auneya/auneya_gate3_full_v116.js'
)


class FullQuorumInteropTests(unittest.TestCase):

    def setUp(self):
        fixture = base.MultiKeeperTests(
            'test_authenticated_quorum_and_determinism'
        )

        fixture.setUp()

        self.addCleanup(
            fixture.doCleanups
        )

        self.fx = fixture
        self.root = fixture.root

        self.cap = (
            self.root /
            'v116-capsule.json'
        )

        portable.export_capsule(
            fixture.trust,
            fixture.b1,
            self.cap
        )

    def call(
        self,
        trust=None,
        cap=None,
        expected=None
    ):
        cap = cap or self.cap

        digest = expected or hashlib.sha256(
            cap.read_bytes()
        ).hexdigest()

        return subprocess.run(
            [
                'node',
                str(NODE),

                '--trust',
                str(trust or self.fx.trust),

                '--capsule',
                str(cap),

                '--expected-capsule',
                digest
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

    def changed(
        self,
        change,
        name='mutated-v116.json'
    ):
        obj = json.loads(
            self.cap.read_text()
        )

        change(obj)

        destination = (
            self.root /
            name
        )

        destination.write_bytes(
            gate.canonical(obj) + b'\n'
        )

        destination.chmod(0o600)

        return destination

    def rejected(self, **kwargs):
        result = self.call(**kwargs)

        self.assertEqual(
            result.returncode,
            2,
            (
                result.stdout,
                result.stderr
            )
        )

        self.assertIn(
            'REJECTED:',
            result.stderr
        )

        self.assertNotIn(
            'AUTHENTICATED_OFFLINE_FULL_QUORUM_RESEARCH',
            result.stdout
        )

    def test_python_node_full_quorum_parity(self):
        python = quorum.run(
            self.fx.trust,
            self.fx.b1
        )

        result = self.call()

        self.assertEqual(
            result.returncode,
            0,
            result.stderr
        )

        output = json.loads(
            result.stdout
        )

        self.assertEqual(
            output['quorum_report_sha256'],
            hashlib.sha256(
                gate.canonical(python)
            ).hexdigest()
        )

        self.assertEqual(
            output['keeper_count'],
            python['keeper_count']
        )

        self.assertEqual(
            output['sequence_decimal'],
            str(python['sequence'])
        )

        self.assertEqual(
            output['anchor_sha256'],
            python['anchor_sha256']
        )

        self.assertTrue(
            output['quorum_signatures_verified']
        )

        for claim in [
            'independent_devices_proven',
            'external_retention_proven',
            'independent_audit_completed',
            'economic_activation',
            'mainnet_active'
        ]:
            self.assertFalse(
                output[claim]
            )

    def test_contiguous_two_checkpoint_history(self):
        import auneya_witness_v110 as witness

        fixture = self.fx

        fixture.commit(
            fixture.db,
            2
        )

        anchor = fixture.checkpoint(
            fixture.db,
            'v116-anchor-two.json',
            fixture.a1
        )

        receipts = []

        for index, (
            private,
            public,
            pin
        ) in enumerate(fixture.keepers):

            receipt = (
                self.root /
                f'v116-receipt-two-{index}.json'
            )

            witness.accept(
                self.root /
                f'keeper-initial-{index}.sqlite',
                anchor,
                fixture.pub,
                fixture.apin,
                private,
                public,
                pin,
                receipt,
                fixture.r1[index][1]
            )

            receipts.append(
                (
                    pin,
                    receipt
                )
            )

        bundle = fixture.bundle(
            'v116-bundle-two.json',
            anchor,
            receipts
        )

        capsule = (
            self.root /
            'v116-second-capsule.json'
        )

        portable.export_capsule(
            fixture.trust,
            bundle,
            capsule,
            fixture.b1
        )

        python = quorum.run(
            fixture.trust,
            bundle,
            fixture.b1
        )

        result = self.call(
            cap=capsule
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr
        )

        output = json.loads(
            result.stdout
        )

        self.assertEqual(
            output['sequence_decimal'],
            '2'
        )

        self.assertEqual(
            output['quorum_report_sha256'],
            hashlib.sha256(
                gate.canonical(python)
            ).hexdigest()
        )

        mutated = json.loads(
            capsule.read_text()
        )

        mutated['previous'] = None

        bad = (
            self.root /
            'v116-missing-history.json'
        )

        bad.write_bytes(
            gate.canonical(mutated) + b'\n'
        )

        bad.chmod(0o600)

        self.rejected(
            cap=bad
        )

    def test_recipient_ack_binds_full_verified_quorum(self):
        import test_auneya_gate3_receipt_v113 as signed_ack

        fixture = signed_ack.Gate3AcceptanceTests(
            'test_signed_acceptance_and_verification'
        )

        fixture.setUp()

        self.addCleanup(
            fixture.doCleanups
        )

        fixture.issue()

        capsule = fixture.fx.path

        args = [
            'node',
            str(NODE),

            '--trust',
            str(fixture.fx.fx.trust),

            '--capsule',
            str(capsule),

            '--expected-capsule',
            hashlib.sha256(
                capsule.read_bytes()
            ).hexdigest(),

            '--receipt',
            str(fixture.path),

            '--recipient-public',
            str(fixture.public),

            '--recipient-pin',
            fixture.pin,

            '--expected-head',
            hashlib.sha256(
                fixture.path.read_bytes()
            ).hexdigest(),

            '--floor',
            str(fixture.fx.floor)
        ]

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr
        )

        self.assertTrue(
            json.loads(
                result.stdout
            )['recipient_ack_verified']
        )

        args[
            args.index('--expected-head') + 1
        ] = 'f' * 64

        bad = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30
        )

        self.assertEqual(
            bad.returncode,
            2
        )

    def test_external_digest_mismatch(self):
        self.rejected(
            expected='f' * 64
        )

    def test_cross_language_report_commitment_tamper(self):
        capsule = self.changed(
            lambda obj: obj.update(
                quorum_report_sha256='0' * 64
            )
        )

        self.rejected(
            cap=capsule
        )

    def test_signed_anchor_substitution(self):

        def change(obj):
            original = base64.b64decode(
                obj['current']['anchor_b64']
            )

            anchor = json.loads(
                original
            )

            anchor['body']['message_count'] += 1

            obj['current']['anchor_b64'] = (
                base64.b64encode(
                    gate.canonical(anchor) + b'\n'
                ).decode()
            )

        self.rejected(
            cap=self.changed(change)
        )

    def test_keeper_signature_forgery(self):

        def change(obj):
            receipt = (
                obj['current']['receipts'][0]
            )

            body = json.loads(
                base64.b64decode(
                    receipt['payload_b64']
                )
            )

            body['signature_b64'] = (
                base64.b64encode(
                    b'\0' * 64
                ).decode()
            )

            receipt['payload_b64'] = (
                base64.b64encode(
                    gate.canonical(body) + b'\n'
                ).decode()
            )

        self.rejected(
            cap=self.changed(change)
        )

    def test_fewer_than_threshold(self):
        self.rejected(
            cap=self.changed(
                lambda obj:
                    obj['current']['receipts'].pop()
            )
        )

    def test_duplicate_keeper(self):
        self.rejected(
            cap=self.changed(
                lambda obj:
                    obj['current']['receipts'].append(
                        obj['current']['receipts'][0]
                    )
            )
        )

    def test_noncanonical_nested_json(self):

        def change(obj):
            receipt = (
                obj['current']['receipts'][0]
            )

            original = base64.b64decode(
                receipt['payload_b64']
            )

            receipt['payload_b64'] = (
                base64.b64encode(
                    original.replace(
                        b'"body":',
                        b'"body":{},"body":',
                        1
                    )
                ).decode()
            )

        self.rejected(
            cap=self.changed(change)
        )

    def test_trust_pin_change(self):
        obj = json.loads(
            self.fx.trust.read_text()
        )

        obj['keepers'][0]['pin'] = (
            'f' * 64
        )

        path = (
            self.root /
            'trust-replaced-v116.json'
        )

        path.write_bytes(
            gate.canonical(obj) + b'\n'
        )

        path.chmod(0o600)

        self.rejected(
            trust=path
        )

    def test_symlink_capsule_refused(self):
        link = (
            self.root /
            'capsule-link-v116.json'
        )

        link.symlink_to(
            self.cap
        )

        self.rejected(
            cap=link
        )


if __name__ == '__main__':
    unittest.main()
