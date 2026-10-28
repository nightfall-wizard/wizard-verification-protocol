"""
Real Ed25519 and SQLite transactional tests.
"""

import copy
from pathlib import Path
import shutil
import sqlite3
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / "tools" / "auneya"),
    str(ROOT / "tests"),
]

import auneya_archive_v10 as v10

from test_auneya_wvp_evidence_batch_v08 import (
    EvidenceBatch,
)


@unittest.skipUnless(
    shutil.which("openssl"),
    "OpenSSL required",
)
class AtomicArchive(unittest.TestCase):

    def setUp(self):

        self.f = EvidenceBatch(
            "test_three_valid_operators"
        )

        self.f.setUp()

        self.addCleanup(
            self.f.doCleanups
        )

        self.a = (
            self.f.root
            / "atomic-replay-and-archive.sqlite"
        )

        self.receipts = [
            self.f.receipt(name)
            for name in self.f.privates
        ]

    def capture(
        self,
        receipts=None,
        pin=None,
        before_commit=None,
    ):

        return v10.capture(
            self.f.challenge,
            (
                self.receipts
                if receipts is None
                else receipts
            ),
            self.f.registry,
            self.f.seal,
            (
                self.f.pin
                if pin is None
                else pin
            ),
            self.a,
            self.f.now,
            before_commit=before_commit,
        )

    def rows(self):

        with sqlite3.connect(self.a) as db:

            return (
                db.execute(
                    "SELECT count(*) FROM receipts"
                ).fetchone()[0],
                db.execute(
                    "SELECT count(*) "
                    "FROM archive_capsules_v10"
                ).fetchone()[0],
            )

    def test_atomic_archive_then_offline_read(self):

        result = self.capture()

        self.assertEqual(
            self.rows(),
            (3, 1),
        )

        digest = result["evidence_sha256"]

        # Delete the original identity registry.
        self.f.registry.unlink()

        obj, proof = v10.inspect_db(
            self.a,
            digest,
            self.f.pin,
        )

        self.assertEqual(
            len(obj["receipts"]),
            3,
        )

        self.assertEqual(
            proof["result"],
            "OFFLINE_SIGNED_STATEMENTS_AUTHENTIC",
        )

        self.assertFalse(
            proof["historical_freshness_proven"]
        )

        exported = (
            self.f.root
            / "independent-capsule.json"
        )

        v10.export(
            self.a,
            digest,
            self.f.pin,
            exported,
        )

        self.assertTrue(
            exported.is_file()
        )

        self.assertEqual(
            exported.stat().st_mode & 0o077,
            0,
        )

        with self.assertRaises(FileExistsError):

            v10.export(
                self.a,
                digest,
                self.f.pin,
                exported,
            )

    def test_replay_rejected_and_old_rows_preserved(self):

        first = self.capture()

        with self.assertRaises(v10.ArchiveError):
            self.capture()

        self.assertEqual(
            self.rows(),
            (3, 1),
        )

        v10.inspect_db(
            self.a,
            first["evidence_sha256"],
            self.f.pin,
        )

    def test_mid_transaction_failure_rolls_back(self):

        def fail():
            raise RuntimeError(
                "injected crash before commit"
            )

        with self.assertRaises(RuntimeError):

            self.capture(
                before_commit=fail
            )

        self.assertEqual(
            self.rows(),
            (0, 0),
        )

        self.capture()

        self.assertEqual(
            self.rows(),
            (3, 1),
        )

    def test_invalid_signature_never_consumes_replay(self):

        altered = copy.deepcopy(
            self.receipts
        )

        altered[0]["status"]["tip"] = (
            "f" * 64
        )

        with self.assertRaises(ValueError):

            self.capture(altered)

        self.assertFalse(
            self.a.exists()
        )

        self.capture()

    def test_wrong_external_pin_rejected(self):

        with self.assertRaises(ValueError):

            self.capture(
                pin="0" * 64
            )

        self.assertFalse(
            self.a.exists()
        )

        result = self.capture()

        with self.assertRaises(ValueError):

            v10.inspect_db(
                self.a,
                result["evidence_sha256"],
                "0" * 64,
            )

    def test_capsule_tamper_or_missing_replay_detected(self):

        result = self.capture()

        with sqlite3.connect(self.a) as db:

            db.execute(
                "DELETE FROM receipts "
                "WHERE node_id=?",
                (
                    self.receipts[0]["node_id"],
                ),
            )

        with self.assertRaises(v10.ArchiveError):

            v10.inspect_db(
                self.a,
                result["evidence_sha256"],
                self.f.pin,
            )

        with sqlite3.connect(self.a) as db:

            db.execute(
                "UPDATE archive_capsules_v10 "
                "SET capsule=?",
                (b'{"malicious":true}',),
            )

        with self.assertRaises(ValueError):

            v10.inspect_db(
                self.a,
                result["evidence_sha256"],
                self.f.pin,
            )


if __name__ == "__main__":
    unittest.main()
