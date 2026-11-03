"""Real Ed25519 v1.11-v1.13 fixtures; simulated devices, NOT real hardware."""

import json
from pathlib import Path
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

import auneya_gate3_audit_v114 as auditor
import auneya_gate3_receipt_v113 as ack
import auneya_capsule_v112 as capsule
import auneya_peer_gate_v16 as gate
import auneya_witness_v110 as keeper

from test_auneya_gate3_receipt_v113 import Gate3AcceptanceTests


class Gate3OfflineAuditTests(unittest.TestCase):

    def setUp(self):

        fixture = Gate3AcceptanceTests(
            'test_signed_acceptance_and_verification'
        )

        fixture.setUp()

        self.addCleanup(
            fixture.doCleanups
        )

        self.fx = fixture
        self.root = fixture.fx.root

        fixture.issue()

        self.rows = [{
            'capsule': fixture.fx.path.name,
            'ack': fixture.path.name
        }]

        self.mfile = self.root / 'audit-manifest.json'

        self.head = gate.sha(
            fixture.path.read_bytes()
        )

        self.manifest()

    def manifest(self):

        self.mfile.write_bytes(
            gate.canonical({
                'format': auditor.FORMAT,
                'entries': self.rows
            }) + b'\n'
        )

    def audit(
        self,
        head=None,
        pin=None,
        floor=None,
        output=None
    ):

        return auditor.inspect(
            self.fx.fx.fx.trust,
            self.mfile,
            self.fx.public,
            pin or self.fx.pin,
            head or self.head,
            floor,
            output
        )

    def test_independent_full_quorum_and_recipient_roundtrip(self):

        result = self.audit(
            floor=self.fx.fx.floor
        )

        self.assertEqual(
            result['entry_count'],
            1
        )

        self.assertTrue(
            result['signatures_verified']
        )

        for forbidden in (
            'independent_devices_proven',
            'external_retention_proven',
            'economic_activation',
            'mainnet_active'
        ):

            self.assertFalse(
                result[forbidden]
            )

    def test_second_signed_sequence_is_a_contiguous_chain(self):

        fx = self.fx.fx.fx

        fx.commit(
            fx.db,
            2
        )

        new_anchor = fx.checkpoint(
            fx.db,
            'audit-anchor2.json',
            fx.a1
        )

        signed = []

        for idx, (priv, pub, pin) in enumerate(fx.keepers):

            dest = (
                self.root /
                f'audit-keeper2-{idx}.json'
            )

            keeper.accept(
                fx.root / f'keeper-initial-{idx}.sqlite',
                new_anchor,
                fx.pub,
                fx.apin,
                priv,
                pub,
                pin,
                dest,
                fx.r1[idx][1]
            )

            signed.append(
                (pin, dest)
            )

        bundle = fx.bundle(
            'audit-bundle2.json',
            new_anchor,
            signed
        )

        second_cap = (
            self.root /
            'audit-capsule2.json'
        )

        capsule.export_capsule(
            fx.trust,
            bundle,
            second_cap,
            fx.b1
        )

        second_ack = (
            self.root /
            'audit-ack2.json'
        )

        ack.issue(
            fx.trust,
            second_cap,
            self.fx.fx.floor,
            self.fx.private,
            self.fx.public,
            self.fx.pin,
            second_ack
        )

        self.rows.append({
            'capsule': second_cap.name,
            'ack': second_ack.name
        })

        self.manifest()

        self.head = gate.sha(
            second_ack.read_bytes()
        )

        result = self.audit(
            floor=self.fx.fx.floor
        )

        self.assertEqual(
            result['entry_count'],
            2
        )

        self.assertEqual(
            result['verified_entries'][1]['sequence'],
            2
        )

        self.rows.reverse()
        self.manifest()

        with self.assertRaises(ValueError):
            self.audit()

    def test_external_head_prevents_complete_history_rollback(self):

        with self.assertRaisesRegex(
            ValueError,
            'head mismatch'
        ):

            self.audit(
                head=(
                    'a' * 64
                    if self.head != 'a' * 64
                    else 'b' * 64
                )
            )

    def test_bad_pin_tampering_and_wrong_trust_fail_closed(self):

        with self.assertRaises(ValueError):

            self.audit(
                pin=(
                    'f' * 64
                    if self.fx.pin != 'f' * 64
                    else 'e' * 64
                )
            )

        raw = json.loads(
            self.fx.path.read_text()
        )

        raw['body']['sequence'] = 3

        self.fx.path.write_bytes(
            gate.canonical(raw) + b'\n'
        )

        with self.assertRaises(ValueError):
            self.audit()

    def test_invalid_path_duplicates_and_noncanonical_manifest(self):

        self.rows[0]['capsule'] = '../escape.json'

        self.manifest()

        with self.assertRaisesRegex(
            ValueError,
            'Unsafe'
        ):
            self.audit()

        self.rows[0]['capsule'] = self.fx.fx.path.name

        self.rows.append(
            dict(self.rows[0])
        )

        self.manifest()

        with self.assertRaises(ValueError):
            self.audit()

        self.mfile.write_text(
            json.dumps(
                {
                    'format': auditor.FORMAT,
                    'entries': self.rows
                },
                indent=2
            ) + '\n'
        )

        with self.assertRaisesRegex(
            ValueError,
            '(?i)noncanonical'
        ):
            self.audit()

    def test_symlink_is_rejected_and_private_output_exclusive(self):

        out = self.root / 'audit-report.json'

        report = self.audit(
            output=out
        )

        self.assertEqual(
            json.loads(out.read_text()),
            report
        )

        with self.assertRaisesRegex(
            ValueError,
            'already exists'
        ):
            self.audit(
                output=out
            )

        out2 = self.root / 'symlink.json'

        out2.symlink_to(
            self.fx.path
        )

        self.rows[0]['ack'] = out2.name

        self.manifest()

        with self.assertRaises(OSError):
            self.audit()

    def test_no_private_signing_material_in_report(self):

        document = gate.canonical(
            self.audit()
        )

        self.assertNotIn(
            b'PRIVATE KEY',
            document
        )

        self.assertNotIn(
            str(self.root).encode(),
            document
        )


if __name__ == '__main__':
    unittest.main()
