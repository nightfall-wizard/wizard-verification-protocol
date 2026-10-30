"""
AUNEYA v1.5 adversarial regression suite.

Uses real Ed25519 evidence and persistent SQLite.
"""

from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / 'tools' / 'auneya'),
    str(ROOT / 'tests')
]

import auneya_admission_v15 as v15
import auneya_archive_v09 as v9
import auneya_federation_v11 as f11
import auneya_nightfall_challenge_v05 as v5
import auneya_portable_v12 as p12
import auneya_registry_checkpoint_v06 as v6
import test_auneya_wvp_evidence_batch_v08 as evidence


class AdmissionLedgerTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(
            prefix='auneya-v15-ledger-'
        )

        self.addCleanup(
            self.tmp.cleanup
        )

        self.p = (
            Path(self.tmp.name) /
            'ledger.sqlite'
        )

        self.one = '1' * 64
        self.two = '2' * 64

    def test_replay_is_durable_across_connections(self):

        v15.commit(
            self.p,
            self.one,
            self.two,
            1000,
            1100
        )

        with self.assertRaisesRegex(
            v15.AdmissionError,
            'REPLAY'
        ):
            v15.commit(
                self.p,
                self.one,
                '3' * 64,
                1001,
                1100
            )

        with sqlite3.connect(self.p) as db:
            self.assertEqual(
                db.execute(
                    'SELECT COUNT(*) FROM accepted'
                ).fetchone()[0],
                1
            )

    def test_rollback_does_not_consume_challenge(self):

        v15.commit(
            self.p,
            self.one,
            self.two,
            1000,
            1100
        )

        with self.assertRaisesRegex(
            v15.AdmissionError,
            'clock rollback'
        ):
            v15.commit(
                self.p,
                '4' * 64,
                '5' * 64,
                999,
                1100
            )

        v15.commit(
            self.p,
            '4' * 64,
            '5' * 64,
            1001,
            1100
        )

    def test_duplicate_manifest_rejected(self):

        v15.commit(
            self.p,
            self.one,
            self.two,
            1000,
            1100
        )

        with self.assertRaisesRegex(
            v15.AdmissionError,
            'REPLAY'
        ):
            v15.commit(
                self.p,
                '3' * 64,
                self.two,
                1001,
                1100
            )

    def test_failed_insert_is_atomic(self):

        v15.commit(
            self.p,
            self.one,
            self.two,
            1000,
            1100
        )

        with sqlite3.connect(self.p) as db:
            db.execute(
                'CREATE TRIGGER fail_insert '
                'BEFORE INSERT ON accepted '
                'BEGIN SELECT '
                "RAISE(ABORT, 'injected'); END;"
            )

        with self.assertRaisesRegex(
            v15.AdmissionError,
            'ledger integrity violation'
        ):
            v15.commit(
                self.p,
                '3' * 64,
                '4' * 64,
                1001,
                1100
            )

        with sqlite3.connect(self.p) as db:
            self.assertEqual(
                db.execute(
                    'SELECT COUNT(*) FROM accepted'
                ).fetchone()[0],
                1
            )

            self.assertEqual(
                db.execute(
                    "SELECT value FROM state "
                    "WHERE name='last_now'"
                ).fetchone()[0],
                1000
            )

    def test_symlink_ledger_refused(self):

        original = (
            Path(self.tmp.name) /
            'original'
        )

        original.write_text('unsafe')

        self.p.symlink_to(original)

        with self.assertRaises(
            v15.AdmissionError
        ):
            v15.commit(
                self.p,
                self.one,
                self.two,
                1000,
                1100
            )

    def test_private_ledger_permissions(self):

        v15.commit(
            self.p,
            self.one,
            self.two,
            1000,
            1100
        )

        self.assertEqual(
            self.p.stat().st_mode & 0o777,
            0o600
        )

        self.p.chmod(0o644)

        with self.assertRaises(
            v15.AdmissionError
        ):
            v15.commit(
                self.p,
                '3' * 64,
                '4' * 64,
                1001,
                1100
            )

    def test_racing_admissions(self):

        v15.commit(
            self.p,
            '0' * 64,
            'f' * 64,
            999,
            1100
        )

        answers = []

        def worker():
            try:
                v15.commit(
                    self.p,
                    self.one,
                    self.two,
                    1000,
                    1100
                )

                answers.append('ok')

            except (
                v15.AdmissionError,
                sqlite3.DatabaseError
            ):
                answers.append('denied')

        threads = [
            threading.Thread(target=worker)
            for _ in range(2)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        self.assertCountEqual(
            answers,
            ['ok', 'denied']
        )


@unittest.skipUnless(
    shutil.which('node')
    and shutil.which('openssl'),
    'Node.js and OpenSSL required'
)
class AdmissionSignedEvidenceTests(unittest.TestCase):

    def setUp(self):

        self.f = evidence.EvidenceBatch(
            'test_three_valid_operators'
        )

        self.f.setUp()

        self.addCleanup(
            self.f.doCleanups
        )

        self.names = list(
            self.f.privates
        )

        self.pin = self.f.pin

        self.ch = f11.sha(
            v5.canonical(
                self.f.challenge
            )
        )

        self.bundle = (
            self.f.root /
            'portable-v15'
        )

        self.ledger = (
            self.f.root /
            'admission.sqlite'
        )

        store = (
            self.f.root /
            'federation-v15.sqlite'
        )

        for i, names in enumerate(
            (
                self.names[:2],
                self.names[1:]
            )
        ):
            capsule = v9.capture(
                self.f.challenge,
                [
                    self.f.receipt(n)
                    for n in names
                ],
                self.f.registry,
                self.f.seal,
                self.pin,
                self.f.root /
                    ('replay-v15-%d.sqlite' % i),
                self.f.now
            )

            source = (
                self.f.root /
                ('source-v15-%d.json' % i)
            )

            v6.write_new(
                source,
                capsule
            )

            f11.ingest(
                store,
                source,
                self.pin,
                self.ch
            )

        exported = p12.export(
            store,
            self.pin,
            self.ch,
            self.bundle
        )

        self.manifest = exported[
            'manifest_sha256'
        ]

    def verify(
        self,
        now=None,
        pin=None,
        manifest=None
    ):
        return v15.admit(
            self.bundle,
            self.pin if pin is None else pin,
            self.ch,
            (
                self.manifest
                if manifest is None
                else manifest
            ),
            self.ledger,
            self.f.now if now is None else now
        )

    def test_real_ed25519_positive_and_replay(self):

        result = self.verify()

        self.assertEqual(
            result['result'],
            'LOCALLY_ADMITTED_ONCE'
        )

        self.assertEqual(
            result['manifest_sha256'],
            self.manifest
        )

        self.assertFalse(
            result['consensus_validated']
        )

        with self.assertRaisesRegex(
            v15.AdmissionError,
            'REPLAY'
        ):
            self.verify()

    def test_expired_challenge_refused(self):

        with self.assertRaisesRegex(
            v15.AdmissionError,
            'outside local admission window'
        ):
            self.verify(
                now=self.f.now + 700
            )

        self.assertFalse(
            self.ledger.exists()
        )

        self.verify()

    def test_future_challenge_refused(self):

        with self.assertRaisesRegex(
            v15.AdmissionError,
            'outside local admission window'
        ):
            self.verify(
                now=self.f.now - 31
            )

        self.assertFalse(
            self.ledger.exists()
        )

    def test_wrong_external_pins_fail_closed(self):

        for argument in (
            {'pin': '0' * 64},
            {'manifest': '0' * 64}
        ):
            with self.subTest(
                argument=argument
            ):
                with self.assertRaises(
                    v15.AdmissionError
                ):
                    self.verify(
                        **argument
                    )

        self.assertFalse(
            self.ledger.exists()
        )

    def test_capsule_tampering_not_admitted(self):

        capfile = next(
            (
                self.bundle /
                'capsules'
            ).iterdir()
        )

        capfile.write_bytes(
            capfile.read_bytes() + b' '
        )

        with self.assertRaises(
            v15.AdmissionError
        ):
            self.verify()

        self.assertFalse(
            self.ledger.exists()
        )

    def test_bundle_symlink_refused(self):

        forged = (
            self.f.root /
            'bundle-link'
        )

        forged.symlink_to(
            self.bundle,
            target_is_directory=True
        )

        with self.assertRaises(
            v15.AdmissionError
        ):
            v15.admit(
                forged,
                self.pin,
                self.ch,
                self.manifest,
                self.ledger,
                self.f.now
            )


if __name__ == '__main__':
    unittest.main()
