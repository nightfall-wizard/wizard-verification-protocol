import copy
import json
from pathlib import Path
import sqlite3
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / 'tools' / 'auneya'),
    str(ROOT / 'tests')
]

import auneya_federation_v11 as f11
import auneya_archive_v09 as v9
import auneya_nightfall_challenge_v05 as v5
import auneya_registry_checkpoint_v06 as v6

from test_auneya_wvp_evidence_batch_v08 import (
    EvidenceBatch,
    status
)


class FederationTests(unittest.TestCase):

    def setUp(self):

        self.f = EvidenceBatch(
            'test_three_valid_operators'
        )

        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

        self.operators = list(self.f.privates)

        self.store = self.f.root / 'federation.sqlite'

        self.challenge_hash = f11.sha(
            v5.canonical(self.f.challenge)
        )

        self.num = 0

    def capsule(self, receipts):

        self.num += 1

        c = v9.capture(
            self.f.challenge,
            receipts,
            self.f.registry,
            self.f.seal,
            self.f.pin,
            self.f.root / (
                'replay-%d.sqlite' % self.num
            ),
            self.f.now
        )

        p = self.f.root / (
            'capsule-%d.json' % self.num
        )

        v6.write_new(p, c)

        return p

    def add(self, p, pin=None, challenge=None):

        return f11.ingest(
            self.store,
            p,
            pin or self.f.pin,
            challenge or self.challenge_hash
        )

    def summary(self):

        return f11.report(
            self.store,
            self.f.pin,
            self.challenge_hash
        )

    def test_union_and_no_double_count(self):

        a, b, c = self.operators

        first = self.capsule([
            self.f.receipt(a),
            self.f.receipt(b)
        ])

        second = self.capsule([
            self.f.receipt(b),
            self.f.receipt(c)
        ])

        self.add(first)
        self.add(second)

        r = self.summary()

        self.assertEqual(r['signer_identity_count'], 3)

        self.assertEqual(
            r['unique_signed_statement_count'],
            3
        )

        self.assertEqual(r['archive_count'], 2)

        self.assertEqual(
            r['observation_verdict'],
            'MATCHING_SIGNED_TIP_CLAIMS'
        )

        self.assertFalse(r['operator_independence_proven'])

        self.assertEqual(
            self.add(first)['result'],
            'ALREADY_IMPORTED'
        )

        self.assertEqual(self.summary(), r)

    def test_order_independent_federation_digest(self):

        a, b, c = self.operators

        files = [
            self.capsule([
                self.f.receipt(a),
                self.f.receipt(b)
            ]),
            self.capsule([
                self.f.receipt(b),
                self.f.receipt(c)
            ])
        ]

        for p in files:
            self.add(p)

        expected = self.summary()

        self.store = (
            self.f.root / 'other-federation.sqlite'
        )

        for p in reversed(files):
            self.add(p)

        self.assertEqual(
            expected,
            self.summary()
        )

    def test_same_signer_conflicting_signed_reports(self):

        a, b, c = self.operators

        first = self.capsule([
            self.f.receipt(a),
            self.f.receipt(b)
        ])

        second = self.capsule([
            self.f.receipt(
                a,
                status(tip='f' * 64)
            ),
            self.f.receipt(c)
        ])

        self.add(first)
        self.add(second)

        out = self.summary()

        self.assertEqual(
            out['observation_verdict'],
            'SAME_SIGNER_CONTRADICTORY_STATEMENTS'
        )

        self.assertEqual(
            out['equivocating_signer_ids'],
            [a]
        )

        self.assertFalse(out['consensus_validated'])

    def test_two_signers_conflicting_tips(self):

        a, b = self.operators[:2]

        p = self.capsule([
            self.f.receipt(a),
            self.f.receipt(
                b,
                status(tip='f' * 64)
            )
        ])

        self.add(p)

        self.assertEqual(
            self.summary()['observation_verdict'],
            'CONFLICTING_SAME_HEIGHT_SIGNED_CLAIMS'
        )

    def test_wrong_pin_and_challenge_rejected_without_store(self):

        a, b = self.operators[:2]

        p = self.capsule([
            self.f.receipt(a),
            self.f.receipt(b)
        ])

        with self.assertRaises(ValueError):
            self.add(p, pin='0' * 64)

        with self.assertRaises(ValueError):
            self.add(p, challenge='f' * 64)

        self.assertFalse(self.store.exists())

    def test_tamper_rejected(self):

        a, b = self.operators[:2]

        p = self.capsule([
            self.f.receipt(a),
            self.f.receipt(b)
        ])

        bad = copy.deepcopy(
            json.loads(p.read_bytes())
        )

        bad['receipts'][0]['status']['tip'] = (
            'f' * 64
        )

        tamper = self.f.root / 'tampered.json'

        v6.write_new(tamper, bad)

        with self.assertRaises(ValueError):
            self.add(tamper)

        self.assertFalse(self.store.exists())

        self.add(p)

        with sqlite3.connect(self.store) as db:
            db.execute(
                'UPDATE federation_capsules_v11 '
                'SET payload=?',
                (b'{}',)
            )

        with self.assertRaises(ValueError):
            self.summary()

    def test_reject_different_registry_anchor_for_challenge(self):

        a, b = self.operators[:2]

        p = self.capsule([
            self.f.receipt(a),
            self.f.receipt(b)
        ])

        self.add(p)

        self.assertEqual(
            self.summary()['archive_count'],
            1
        )

        with self.assertRaises(ValueError):
            f11.report(
                self.store,
                '0' * 64,
                self.challenge_hash
            )

    def test_shared_key_across_captures_not_independent(self):

        a, b, c = self.operators

        alias = 'node_research_operator_alias'

        self.f.add_operator(alias, share=a)

        new_seal = (
            self.f.root / 'new-checkpoint.json'
        )

        self.f.pin = v6.write_new(
            new_seal,
            v6.snapshot(self.f.registry)
        )

        self.f.seal = new_seal

        first = self.capsule([
            self.f.receipt(a),
            self.f.receipt(b)
        ])

        second = self.capsule([
            self.f.receipt(alias),
            self.f.receipt(c)
        ])

        self.add(first)
        self.add(second)

        r = self.summary()

        self.assertEqual(
            r['observation_verdict'],
            'DUPLICATE_PUBLIC_KEY_IDENTITIES'
        )

        self.assertIn(
            [a, alias],
            r['duplicate_public_key_identities']
        )

        self.assertEqual(
            r['distinct_key_count'],
            3
        )


if __name__ == '__main__':
    unittest.main()
