import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / 'tools' / 'auneya'),
    str(ROOT / 'tests')
]

import auneya_portable_v12 as p12
import auneya_federation_v11 as f11
import auneya_archive_v09 as v9
import auneya_nightfall_challenge_v05 as v5
import auneya_registry_checkpoint_v06 as v6

from test_auneya_wvp_evidence_batch_v08 import EvidenceBatch


class PortableFederationTests(unittest.TestCase):

    def setUp(self):

        self.f = EvidenceBatch(
            'test_three_valid_operators'
        )

        self.f.setUp()

        self.addCleanup(
            self.f.doCleanups
        )

        self.ops = list(
            self.f.privates
        )

        self.store = (
            self.f.root / 'federation.sqlite'
        )

        self.challenge_hash = f11.sha(
            v5.canonical(self.f.challenge)
        )

        self.pin = self.f.pin

        self.bundle = (
            self.f.root / 'portable-bundle'
        )

    def capsule(self, names, i):

        o = v9.capture(
            self.f.challenge,
            [self.f.receipt(x) for x in names],
            self.f.registry,
            self.f.seal,
            self.f.pin,
            self.f.root / (
                'replay-%s.sqlite' % i
            ),
            self.f.now
        )

        path = self.f.root / (
            'capsule-%s.json' % i
        )

        v6.write_new(path, o)

        return path

    def prepare(self):

        a, b, c = self.ops

        for i, ids in enumerate(
            ([a, b], [b, c])
        ):

            cap = self.capsule(
                ids,
                i
            )

            f11.ingest(
                self.store,
                cap,
                self.pin,
                self.challenge_hash
            )

        return p12.export(
            self.store,
            self.pin,
            self.challenge_hash,
            self.bundle
        )

    def check(self, digest):

        return p12.verify(
            self.bundle,
            self.pin,
            self.challenge_hash,
            digest
        )

    def test_export_and_verify_independently(self):

        result = self.prepare()

        verified = self.check(
            result['manifest_sha256']
        )

        self.assertEqual(
            verified['capsule_count'],
            2
        )

        self.assertEqual(
            verified['observation_verdict'],
            'MATCHING_SIGNED_TIP_CLAIMS'
        )

        self.assertFalse(
            verified['security_boundary'][
                'consensus_validated'
            ]
        )

    def test_reject_overwriting_existing_bundle(self):

        self.prepare()

        with self.assertRaises(ValueError):

            p12.export(
                self.store,
                self.pin,
                self.challenge_hash,
                self.bundle
            )

    def test_corrupted_capsule_rejected(self):

        digest = self.prepare()[
            'manifest_sha256'
        ]

        cap = next(
            (self.bundle / 'capsules').iterdir()
        )

        cap.write_bytes(b'{}')

        with self.assertRaises(ValueError):
            self.check(digest)

    def test_wrong_independent_pins_rejected(self):

        digest = self.prepare()[
            'manifest_sha256'
        ]

        with self.assertRaises(ValueError):

            p12.verify(
                self.bundle,
                '0' * 64,
                self.challenge_hash,
                digest
            )

        with self.assertRaises(ValueError):

            p12.verify(
                self.bundle,
                self.pin,
                '0' * 64,
                digest
            )

        with self.assertRaises(ValueError):
            self.check('0' * 64)

    def test_extra_file_is_rejected(self):

        digest = self.prepare()[
            'manifest_sha256'
        ]

        (
            self.bundle / 'unexpected'
        ).write_text('x')

        with self.assertRaises(ValueError):
            self.check(digest)

    def test_missing_capsule_is_rejected(self):

        digest = self.prepare()[
            'manifest_sha256'
        ]

        next(
            (self.bundle / 'capsules').iterdir()
        ).unlink()

        with self.assertRaises(
            (ValueError, OSError)
        ):
            self.check(digest)

    def test_duplicate_manifest_entry_rejected_even_with_new_pin(self):

        self.prepare()

        f = self.bundle / 'manifest.json'

        obj = json.loads(
            f.read_bytes()
        )

        obj['capsules'].append(
            copy.deepcopy(
                obj['capsules'][0]
            )
        )

        raw = v6.canonical(obj)

        f.write_bytes(raw)

        with self.assertRaises(ValueError):

            self.check(
                f11.sha(raw)
            )

    def test_fake_report_rejected_even_with_new_manifest_hash(self):

        self.prepare()

        f = self.bundle / 'manifest.json'

        obj = json.loads(
            f.read_bytes()
        )

        obj['federation_report'][
            'signer_identity_count'
        ] = 400

        raw = v6.canonical(obj)

        f.write_bytes(raw)

        with self.assertRaises(ValueError):

            self.check(
                f11.sha(raw)
            )

    def test_symbolic_link_capsule_rejected(self):

        digest = self.prepare()[
            'manifest_sha256'
        ]

        cap = next(
            (self.bundle / 'capsules').iterdir()
        )

        original = (
            self.f.root / 'held.json'
        )

        cap.rename(original)

        cap.symlink_to(original)

        with self.assertRaises(
            (ValueError, OSError)
        ):
            self.check(digest)

    def test_order_independent_export_manifest(self):

        first = self.prepare()

        a, b, c = self.ops

        other = (
            self.f.root / 'reverse.sqlite'
        )

        for i, ids in enumerate(
            ([b, c], [a, b])
        ):

            f11.ingest(
                other,
                self.capsule(ids, i + 2),
                self.pin,
                self.challenge_hash
            )

        second_bundle = (
            self.f.root / 'second-bundle'
        )

        second = p12.export(
            other,
            self.pin,
            self.challenge_hash,
            second_bundle
        )

        self.assertEqual(
            first['manifest_sha256'],
            second['manifest_sha256']
        )


if __name__ == '__main__':
    unittest.main()
