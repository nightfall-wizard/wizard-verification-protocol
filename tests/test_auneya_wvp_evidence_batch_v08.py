"""
Real Ed25519 and SQLite adversarial tests.
"""

from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "tools"
        / "auneya"
    ),
)

import auneya_nightfall_challenge_v05 as v5
import auneya_registry_checkpoint_v06 as v6
import auneya_trusted_node_identity_v04 as ids
import auneya_wvp_evidence_batch_v08 as v8


def status(tip="a" * 64, height=25000):

    return {

        "network": "mainnet",

        "genesis": v5.GENESIS,

        "protocol_version": 8,

        "tip_height": height,

        "tip": tip,

        "total_work": "9000000",

        "live_peers": 2,

        "best_peer_height": height,

        "supply_invariant_ok": True,

        "loading": False,

        "stalled_on_fork": False,

        "reorg_in_flight": False,
    }


@unittest.skipUnless(
    shutil.which("openssl"),
    "real Ed25519 requires OpenSSL",
)
class EvidenceBatch(unittest.TestCase):

    def setUp(self):

        self.temp = tempfile.TemporaryDirectory(
            prefix="auneya-v08-test-"
        )

        self.addCleanup(
            self.temp.cleanup
        )

        self.root = Path(self.temp.name)

        self.registry = (
            self.root / "identity.sqlite"
        )

        self.seal = (
            self.root / "checkpoint.json"
        )

        self.replay = (
            self.root / "replay.sqlite"
        )

        self.now = int(time.time())

        self.challenge = v5.new_challenge(
            self.now
        )

        self.privates = {}

        for name in (

            "node_research_operator_a",

            "node_research_operator_b",

            "node_research_operator_c",

        ):

            self.add_operator(name)

        self.pin = v6.write_new(

            self.seal,

            v6.snapshot(self.registry),

        )

    def add_operator(
        self,
        name,
        share=None,
    ):

        if share:

            private, public = (
                self.privates[share]
            )

        else:

            private = (
                self.root
                / (name + ".private.pem")
            )

            public = (
                self.root
                / (name + ".public.pem")
            )

            subprocess.run(

                [
                    "openssl",
                    "genpkey",
                    "-algorithm",
                    "ED25519",
                    "-out",
                    str(private),
                ],

                check=True,

                capture_output=True,

            )

            private.chmod(0o600)

            subprocess.run(

                [
                    "openssl",
                    "pkey",
                    "-in",
                    str(private),
                    "-pubout",
                    "-out",
                    str(public),
                ],

                check=True,

                capture_output=True,

            )

        ids.enroll(

            self.registry,

            name,

            public,

            ids.fingerprint(
                ids.key_der(public)
            ),

        )

        self.privates[name] = (
            private,
            public,
        )

    def receipt(
        self,
        name,
        public_status=None,
    ):

        return v5.attest(

            self.challenge,

            name,

            self.privates[name][0],

            (
                status()
                if public_status is None
                else public_status
            ),

            self.now,

        )

    def check(
        self,
        receipts,
        replay=None,
        pin=None,
    ):

        return v8.verify_batch(

            self.challenge,

            receipts,

            self.registry,

            self.seal,

            (
                self.pin
                if pin is None
                else pin
            ),

            (
                self.replay
                if replay is None
                else replay
            ),

            self.now,

        )

    def test_three_valid_operators(self):

        receipts = [

            self.receipt(name)

            for name in self.privates

        ]

        report = self.check(receipts)

        self.assertEqual(
            report["operator_count"],
            3,
        )

        self.assertEqual(

            report["observation_verdict"],

            "MATCHING_SIGNED_TIP_CLAIMS",

        )

        self.assertFalse(
            report["consensus_validated"]
        )

        self.assertFalse(
            report["independent_devices_proven"]
        )

        self.assertEqual(

            report["pairwise_results"][
                "MATCHING_TIP_CLAIMS"
            ],

            3,

        )

        with self.assertRaises(
            v5.ChallengeError
        ):

            self.check(receipts)

    def test_conflicting_same_height(self):

        names = list(self.privates)

        receipts = [

            self.receipt(names[0]),

            self.receipt(
                names[1],
                status("b" * 64),
            ),

            self.receipt(names[2]),

        ]

        report = self.check(receipts)

        self.assertEqual(

            report["observation_verdict"],

            "CONFLICTING_SAME_HEIGHT_SIGNED_CLAIMS",

        )

        self.assertFalse(
            report["consensus_validated"]
        )

    def test_differing_heights(self):

        names = list(self.privates)

        report = self.check([

            self.receipt(names[0]),

            self.receipt(

                names[1],

                status(
                    "b" * 64,
                    height=25001,
                ),

            ),

        ])

        self.assertEqual(

            report["observation_verdict"],

            "DIVERGENT_SIGNED_CLAIMS_NOT_FORK_PROOF",

        )

    def test_invalid_signature_atomicity(self):

        names = list(self.privates)

        receipts = [

            self.receipt(name)

            for name in names

        ]

        altered = {

            **receipts[2],

            "status": {

                **receipts[2]["status"],

                "tip": "f" * 64,

            },

        }

        with self.assertRaises(
            v5.ChallengeError
        ):

            self.check([

                receipts[0],

                receipts[1],

                altered,

            ])

        self.assertFalse(
            self.replay.exists()
        )

        self.check(receipts)

    def test_duplicate_signer(self):

        first = list(self.privates)[0]

        receipt = self.receipt(first)

        with self.assertRaises(
            v8.BatchError
        ):

            self.check([
                receipt,
                receipt,
            ])

        self.assertFalse(
            self.replay.exists()
        )

    def test_shared_public_key_rejected(self):

        first = list(self.privates)[0]

        alias = "node_research_operator_alias"

        self.add_operator(
            alias,
            share=first,
        )

        revised = (
            self.root / "revised.json"
        )

        self.pin = v6.write_new(

            revised,

            v6.snapshot(self.registry),

        )

        self.seal = revised

        with self.assertRaises(
            v8.BatchError
        ):

            self.check([

                self.receipt(first),

                self.receipt(alias),

            ])

        self.assertFalse(
            self.replay.exists()
        )

    def test_bad_pin(self):

        names = list(self.privates)[:2]

        receipts = [

            self.receipt(name)

            for name in names

        ]

        with self.assertRaises(
            v6.CheckpointError
        ):

            self.check(
                receipts,
                pin="0" * 64,
            )

        self.assertFalse(
            self.replay.exists()
        )

        self.check(receipts)

    def test_registry_mutation(self):

        first = list(self.privates)[0]

        with sqlite3.connect(
            self.registry
        ) as db:

            db.execute(

                "UPDATE nodes "
                "SET state='revoked' "
                "WHERE node_id=?",

                (first,),

            )

        with self.assertRaises(
            (
                v8.BatchError,
                v6.CheckpointError,
            )
        ):

            self.check([

                self.receipt(name)

                for name
                in list(self.privates)[:2]

            ])

        self.assertFalse(
            self.replay.exists()
        )

    def test_order_independent_commitment(self):

        receipts = [

            self.receipt(name)

            for name in self.privates

        ]

        first = self.check(receipts)

        second = self.check(

            list(reversed(receipts)),

            replay=(
                self.root
                / "another-replay.sqlite"
            ),

        )

        self.assertEqual(

            first["evidence_sha256"],

            second["evidence_sha256"],

        )

        self.assertEqual(

            first["claimed_tip_groups"],

            second["claimed_tip_groups"],

        )

    def test_expiry_and_limit(self):

        receipts = [

            self.receipt(name)

            for name
            in list(self.privates)[:2]

        ]

        with self.assertRaises(
            v5.ChallengeError
        ):

            v8.verify_batch(

                self.challenge,

                receipts,

                self.registry,

                self.seal,

                self.pin,

                self.replay,

                self.now + 1000,

            )

        with self.assertRaises(
            v8.BatchError
        ):

            self.check(
                receipts * 9
            )

        self.assertFalse(
            self.replay.exists()
        )


if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )
