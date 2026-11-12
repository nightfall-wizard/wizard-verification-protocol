import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT / 'tests'),
    str(ROOT / 'tools/auneya')
]

import test_auneya_quorum_v111 as source
import auneya_capsule_v112 as capsule
import auneya_guard_v121 as guard


class Gate4DifferentialTests(unittest.TestCase):
    def setUp(self):
        base = source.MultiKeeperTests(
            'test_authenticated_quorum_and_determinism'
        )
        base.setUp()
        self.addCleanup(base.doCleanups)

        self.base = base
        self.capsule = base.root / 'v121-test-capsule.json'

        capsule.export_capsule(
            base.trust,
            base.b1,
            self.capsule
        )

        self.digest = hashlib.sha256(
            self.capsule.read_bytes()
        ).hexdigest()

    def test_corpus_unique_and_deterministic(self):
        before = self.capsule.read_bytes()
        first = guard.mutants(before)
        second = guard.mutants(before)

        self.assertEqual(first, second)
        self.assertGreaterEqual(len(first), 100)
        self.assertEqual(
            len({hashlib.sha256(data).digest() for _, data in first}),
            len(first)
        )
        self.assertEqual(self.capsule.read_bytes(), before)

    def test_real_signed_dual_runtime_campaign(self):
        before = self.capsule.read_bytes()

        report = guard.build(
            str(self.base.trust),
            str(self.capsule),
            self.digest
        )

        self.assertGreaterEqual(report['cases_passed'], 100)
        self.assertTrue(
            all(
                item['python_rejected'] and item['node_rejected']
                for item in report['cases']
            )
        )
        self.assertFalse(report['physical_device_independence_proven'])
        self.assertFalse(report['mainnet_active'])
        self.assertFalse(report['economic_activation'])
        self.assertEqual(before, self.capsule.read_bytes())

    def test_refuses_unpinned_source(self):
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            guard.build(
                str(self.base.trust),
                str(self.capsule),
                '0' * 64
            )


if __name__ == '__main__':
    unittest.main()
