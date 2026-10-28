import copy
import sys
import unittest

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / 'tools' / 'auneya'),
    str(ROOT / 'tests'),
]

import auneya_archive_v09 as v9

from test_auneya_wvp_evidence_batch_v08 import (
    EvidenceBatch,
)


class ArchiveTests(unittest.TestCase):

    def setUp(self):

        self.f = EvidenceBatch(
            'test_three_valid_operators'
        )

        self.f.setUp()

        self.addCleanup(
            self.f.doCleanups
        )

    def test_authentic_archive_and_tamper(self):

        f = self.f

        receipts = [
            f.receipt(n)
            for n in f.privates
        ]

        capsule = v9.capture(
            f.challenge,
            receipts,
            f.registry,
            f.seal,
            f.pin,
            f.replay,
            f.now,
        )

        result = v9.inspect(
            capsule,
            f.pin,
        )

        self.assertFalse(
            result['historical_freshness_proven']
        )

        f.registry.unlink()

        result = v9.inspect(
            capsule,
            f.pin,
        )

        self.assertEqual(
            result['result'],
            'OFFLINE_SIGNED_STATEMENTS_AUTHENTIC',
        )

        bad = copy.deepcopy(capsule)

        bad['receipts'][0]['status']['tip'] = (
            'f' * 64
        )

        with self.assertRaises(ValueError):
            v9.inspect(bad, f.pin)

        bad = copy.deepcopy(capsule)

        bad['report']['consensus_validated'] = True

        with self.assertRaises(ValueError):
            v9.inspect(bad, f.pin)

        with self.assertRaises(ValueError):
            v9.inspect(capsule, '0' * 64)


if __name__ == '__main__':
    unittest.main()
