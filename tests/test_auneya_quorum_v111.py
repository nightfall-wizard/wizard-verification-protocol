"""
AUNEYA v1.11 adversarial regression tests.

Real Ed25519 keys.
Real signed anchors.
Real signed keeper receipts.

Local isolated stores do not prove
physical device independence.
"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "tools" / "auneya")
)

import auneya_peer_gate_v16 as gate
import auneya_anchor_v19 as anchor
import auneya_witness_v110 as witness
import auneya_quorum_v111 as quorum


NODE_KEYS = r"""
const crypto = require('node:crypto');

const key = crypto.generateKeyPairSync('ed25519');

console.log(JSON.stringify({
    private: key.privateKey.export({
        format: 'pem',
        type: 'pkcs8'
    }),
    public: key.publicKey.export({
        format: 'pem',
        type: 'spki'
    })
}));
"""


class MultiKeeperTests(unittest.TestCase):

    def setUp(self):

        tmp = tempfile.TemporaryDirectory(
            prefix="auneya-v111-"
        )

        self.addCleanup(
            tmp.cleanup
        )

        self.root = Path(tmp.name)

        self.root.chmod(
            0o700
        )

        self.chain = "auneya-research-v1"

        self.priv, self.pub, self.apin = (
            self.key("producer")
        )

        self.keepers = [
            self.key("keeper-0"),
            self.key("keeper-1")
        ]

        self.db = self.root / "replay.sqlite"

        self.commit(
            self.db,
            1
        )

        self.a1 = self.checkpoint(
            self.db,
            "anchor-1.json"
        )

        self.r1 = self.receipts(
            self.a1,
            "initial"
        )

        self.trust = self.write(
            "trust.json",
            {
                "format": quorum.TRUST_FORMAT,

                "chain_id": self.chain,

                "anchor_public": str(self.pub),

                "anchor_pin": self.apin,

                "threshold": 2,

                "keepers": [
                    {
                        "pin": pin,
                        "public": str(public)
                    }

                    for _, public, pin in self.keepers
                ]
            }
        )

        self.b1 = self.bundle(
            "bundle-1.json",
            self.a1,
            self.r1
        )

    def write(self, name, data):

        path = self.root / name

        path.write_bytes(
            gate.canonical(data) + b"\n"
        )

        path.chmod(
            0o600
        )

        return path

    def key(self, name):

        raw = json.loads(
            subprocess.check_output(
                [
                    "node",
                    "-e",
                    NODE_KEYS
                ]
            )
        )

        private = (
            self.root /
            (name + "-private.pem")
        )

        public = (
            self.root /
            (name + "-public.pem")
        )

        private.write_text(
            raw["private"]
        )

        public.write_text(
            raw["public"]
        )

        private.chmod(
            0o600
        )

        public.chmod(
            0o600
        )

        return (
            private,
            public,
            gate.sha(public.read_bytes())
        )

    def commit(self, db, number, variant=0):

        gate.commit(
            db,
            {
                "chain_id": self.chain,

                "sender": "phone-alpha",

                "epoch": 1,

                "counter": number,

                "challenge_sha256":
                    f"{number + variant:064x}",

                "manifest_sha256":
                    f"{number + 100:064x}"
            },

            1000 + number
        )

    def checkpoint(
        self,
        db,
        name,
        previous=None
    ):

        dest = self.root / name

        anchor.capture(
            db,
            dest,
            self.priv,
            self.pub,
            self.apin,
            self.chain,
            previous
        )

        return dest

    def receipts(
        self,
        checkpoint,
        suffix
    ):

        output = []

        for idx, (
            private,
            public,
            pin
        ) in enumerate(self.keepers):

            dest = (
                self.root /
                f"receipt-{suffix}-{idx}.json"
            )

            witness.accept(
                self.root /
                    f"keeper-{suffix}-{idx}.sqlite",

                checkpoint,
                self.pub,
                self.apin,
                private,
                public,
                pin,
                dest
            )

            output.append(
                (pin, dest)
            )

        return output

    def bundle(
        self,
        name,
        checkpoint,
        receipts
    ):

        return self.write(
            name,
            {
                "format": quorum.BUNDLE_FORMAT,

                "anchor": str(checkpoint),

                "receipts": [
                    {
                        "pin": pin,
                        "path": str(path)
                    }

                    for pin, path in receipts
                ]
            }
        )

    def test_authenticated_quorum_and_determinism(self):

        first = quorum.run(
            self.trust,
            self.b1
        )

        second = quorum.run(
            self.trust,
            self.b1
        )

        self.assertEqual(
            first,
            second
        )

        self.assertEqual(
            first["keeper_count"],
            2
        )

        self.assertEqual(
            first["required_quorum"],
            2
        )

        self.assertTrue(
            first["signatures_verified"]
        )

        self.assertFalse(
            first["independent_devices_proven"]
        )

        self.assertFalse(
            first["economic_activation"]
        )

    def test_insufficient_quorum_and_duplicate_identity(self):

        partial = self.bundle(
            "partial.json",
            self.a1,
            self.r1[:1]
        )

        with self.assertRaisesRegex(
            ValueError,
            "insufficient signed quorum"
        ):

            quorum.run(
                self.trust,
                partial
            )

        duplicate = self.bundle(
            "duplicate.json",
            self.a1,
            [self.r1[0]] * 2
        )

        with self.assertRaisesRegex(
            ValueError,
            "duplicate keeper"
        ):

            quorum.run(
                self.trust,
                duplicate
            )

    def test_forged_receipt_and_unknown_signer(self):

        bad = self.root / "corrupt.json"

        bad.write_bytes(
            self.r1[0][1].read_bytes().replace(
                b'"sequence":1',
                b'"sequence":2'
            )
        )

        bad.chmod(
            0o600
        )

        modified = self.bundle(
            "modified.json",
            self.a1,
            [
                (self.r1[0][0], bad),
                self.r1[1]
            ]
        )

        with self.assertRaises(ValueError):

            quorum.run(
                self.trust,
                modified
            )

        unknown = self.bundle(
            "unknown.json",
            self.a1,
            [
                ("f" * 64, self.r1[0][1]),
                self.r1[1]
            ]
        )

        with self.assertRaisesRegex(
            ValueError,
            "unknown keeper"
        ):

            quorum.run(
                self.trust,
                unknown
            )

    def test_successor_link_and_rollback_failure(self):

        self.commit(
            self.db,
            2
        )

        a2 = self.checkpoint(
            self.db,
            "anchor-2.json",
            self.a1
        )

        r2 = []

        for idx, (
            private,
            public,
            pin
        ) in enumerate(self.keepers):

            dest = (
                self.root /
                f"receipt-next-{idx}.json"
            )

            witness.accept(
                self.root /
                    f"keeper-initial-{idx}.sqlite",

                a2,
                self.pub,
                self.apin,
                private,
                public,
                pin,
                dest,
                self.r1[idx][1]
            )

            r2.append(
                (pin, dest)
            )

        b2 = self.bundle(
            "bundle-2.json",
            a2,
            r2
        )

        result = quorum.run(
            self.trust,
            b2,
            self.b1
        )

        self.assertEqual(
            result["sequence"],
            2
        )

        with self.assertRaisesRegex(
            ValueError,
            "requires previous"
        ):

            quorum.run(
                self.trust,
                b2
            )

        with self.assertRaisesRegex(
            ValueError,
            "rollback|skipped"
        ):

            quorum.run(
                self.trust,
                self.b1,
                b2
            )

    def test_cryptographically_signed_equivocation_detected(self):

        alternate = (
            self.root /
            "alternate.sqlite"
        )

        self.commit(
            alternate,
            1,
            variant=9
        )

        fork = self.checkpoint(
            alternate,
            "anchor-fork.json"
        )

        fork_receipts = self.receipts(
            fork,
            "fork"
        )

        other = self.bundle(
            "bundle-fork.json",
            fork,
            fork_receipts
        )

        with self.assertRaisesRegex(
            ValueError,
            "EQUIVOCATION"
        ):

            quorum.run(
                self.trust,
                self.b1,
                compare_path=other
            )

    def test_key_pin_mismatch_and_noncanonical_manifest(self):

        obj = json.loads(
            self.trust.read_text()
        )

        obj["keepers"][0]["pin"] = "f" * 64

        bad_trust = self.write(
            "wrong-trust.json",
            obj
        )

        with self.assertRaisesRegex(
            ValueError,
            "pin mismatch"
        ):

            quorum.run(
                bad_trust,
                self.b1
            )

        bad_bundle = (
            self.root /
            "noncanonical.json"
        )

        bad_bundle.write_text(
            json.dumps(
                json.loads(
                    self.b1.read_text()
                ),
                indent=2
            ) + "\n"
        )

        bad_bundle.chmod(
            0o600
        )

        with self.assertRaisesRegex(
            ValueError,
            "canonical"
        ):

            quorum.run(
                self.trust,
                bad_bundle
            )


if __name__ == "__main__":
    unittest.main()
