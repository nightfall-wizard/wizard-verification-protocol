"""
AUNEYA v1.12 adversarial regression tests.

Real Ed25519 keys and signed v1.11 evidence.
"""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "tools" / "auneya")
)

sys.path.insert(
    0,
    str(ROOT / "tests")
)

import auneya_peer_gate_v16 as gate
import auneya_witness_v110 as witness
import auneya_capsule_v112 as portable
import test_auneya_quorum_v111 as fixtures


class PortableCapsuleTests(unittest.TestCase):

    def setUp(self):
        fixture = fixtures.MultiKeeperTests(
            "test_authenticated_quorum_and_determinism"
        )

        fixture.setUp()

        self.addCleanup(
            fixture.doCleanups
        )

        self.fx = fixture
        self.root = fixture.root

        self.path = (
            self.root / "exchange-v112.json"
        )

        self.floor = (
            self.root / "highwater-v112.json"
        )

        portable.export_capsule(
            fixture.trust,
            fixture.b1,
            self.path
        )

    def saved(self, obj, name):
        file = self.root / name

        file.write_bytes(
            gate.canonical(obj) + b"\n"
        )

        file.chmod(0o600)

        return file

    def record(self):
        return json.loads(
            self.path.read_text()
        )

    def test_round_trip_and_highwater_idempotency(self):
        out = portable.verify_capsule(
            self.fx.trust,
            self.path,
            self.floor
        )

        self.assertEqual(
            out["floor_status"],
            "initialized"
        )

        self.assertEqual(
            out["keeper_count"],
            2
        )

        self.assertEqual(
            out["sequence"],
            1
        )

        again = portable.verify_capsule(
            self.fx.trust,
            self.path,
            self.floor
        )

        self.assertEqual(
            again["floor_status"],
            "unchanged"
        )

        self.assertFalse(
            out["independent_devices_proven"]
        )

        self.assertFalse(
            out["economic_activation"]
        )

        self.assertFalse(
            out["external_retention_proven"]
        )

    def test_modified_signed_receipt_fails_closed(self):
        obj = self.record()

        data = portable.decoded(
            obj["current"]["receipts"][0]["payload_b64"],
            16 * 1024
        )

        corrupted = bytearray(data)
        corrupted[-6] ^= 1

        obj["current"]["receipts"][0]["payload_b64"] = (
            portable.encoded(corrupted)
        )

        altered = self.saved(
            obj,
            "modified.json"
        )

        with self.assertRaises(ValueError):
            portable.verify_capsule(
                self.fx.trust,
                altered
            )

    def test_duplicate_keeper_and_noncanonical_input_refused(self):
        obj = self.record()

        obj["current"]["receipts"].append(
            obj["current"]["receipts"][0]
        )

        with self.assertRaises(ValueError):
            portable.verify_capsule(
                self.fx.trust,
                self.saved(
                    obj,
                    "duplicate.json"
                )
            )

        wrong = (
            self.root / "noncanonical-capsule.json"
        )

        wrong.write_text(
            json.dumps(
                self.record(),
                indent=2
            ) + "\n"
        )

        wrong.chmod(0o600)

        with self.assertRaisesRegex(
            ValueError,
            "noncanonical"
        ):
            portable.verify_capsule(
                self.fx.trust,
                wrong
            )

    def test_policy_is_not_embedded_and_pin_mismatch_fails(self):
        raw = self.path.read_bytes()

        self.assertNotIn(
            b"PRIVATE KEY",
            raw
        )

        self.assertNotIn(
            str(self.root).encode(),
            raw
        )

        policy = json.loads(
            self.fx.trust.read_text()
        )

        policy["keepers"][0]["pin"] = (
            "f" * 64
        )

        bad = self.saved(
            policy,
            "bad-trust.json"
        )

        with self.assertRaises(ValueError):
            portable.verify_capsule(
                bad,
                self.path
            )

    def test_floor_rejects_rollback_and_wrong_predecessor(self):
        portable.verify_capsule(
            self.fx.trust,
            self.path,
            self.floor
        )

        fixture = self.fx

        fixture.commit(
            fixture.db,
            2
        )

        new_anchor = fixture.checkpoint(
            fixture.db,
            "anchor-2-new.json",
            fixture.a1
        )

        receipts = []

        for idx, (
            private,
            public,
            pin
        ) in enumerate(fixture.keepers):

            receipt = (
                self.root /
                f"new-receipt-{idx}.json"
            )

            witness.accept(
                fixture.root /
                f"keeper-initial-{idx}.sqlite",
                new_anchor,
                fixture.pub,
                fixture.apin,
                private,
                public,
                pin,
                receipt,
                fixture.r1[idx][1]
            )

            receipts.append(
                (pin, receipt)
            )

        new_bundle = fixture.bundle(
            "new-bundle.json",
            new_anchor,
            receipts
        )

        new_pack = (
            self.root /
            "exchange-second.json"
        )

        portable.export_capsule(
            fixture.trust,
            new_bundle,
            new_pack,
            fixture.b1
        )

        result = portable.verify_capsule(
            fixture.trust,
            new_pack,
            self.floor
        )

        self.assertEqual(
            result["floor_status"],
            "advanced"
        )

        self.assertEqual(
            result["sequence"],
            2
        )

        with self.assertRaisesRegex(
            ValueError,
            "STALE"
        ):
            portable.verify_capsule(
                fixture.trust,
                self.path,
                self.floor
            )

        altered = self.record()

        altered["current"]["anchor_b64"] = (
            portable.encoded(
                fixture.a1.read_bytes()[:-4]
                + b"BAD!"
            )
        )

        with self.assertRaises(ValueError):
            portable.verify_capsule(
                fixture.trust,
                self.saved(
                    altered,
                    "fork.json"
                ),
                self.floor
            )

    def test_no_replacement_of_existing_output(self):
        before = self.path.read_bytes()

        with self.assertRaises(FileExistsError):
            portable.export_capsule(
                self.fx.trust,
                self.fx.b1,
                self.path
            )

        self.assertEqual(
            before,
            self.path.read_bytes()
        )

    def test_truncated_and_oversized_refused(self):
        path = (
            self.root / "trunc.json"
        )

        path.write_bytes(
            self.path.read_bytes()[:-1]
        )

        path.chmod(0o600)

        with self.assertRaises(ValueError):
            portable.verify_capsule(
                self.fx.trust,
                path
            )

        with self.assertRaises(ValueError):
            portable.decoded(
                "A" * (4 * 1024 * 1024),
                16384
            )


if __name__ == "__main__":
    unittest.main()
