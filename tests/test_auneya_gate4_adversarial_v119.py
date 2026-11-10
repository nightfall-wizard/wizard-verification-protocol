"""Real Ed25519 two-keeper v1.19 adversarial dual-runtime conformance."""
import hashlib
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT / 'tools/auneya')]

import auneya_capsule_v112 as cap
import auneya_gate4_adversarial_v119 as campaign
import test_auneya_quorum_v111 as fixture


class AdversarialCampaignTests(unittest.TestCase):
    def setUp(self):
        base = fixture.MultiKeeperTests('test_authenticated_quorum_and_determinism')
        base.setUp()
        self.addCleanup(base.doCleanups)
        self.base = base
        self.path = base.root / 'v119-capsule.json'
        cap.export_capsule(base.trust, base.b1, self.path)
        self.digest = hashlib.sha256(self.path.read_bytes()).hexdigest()

    def test_all_real_cryptographic_mutants_rejected(self):
        result = campaign.run(str(self.base.trust), str(self.path), self.digest)
        self.assertEqual(result['format'], campaign.FORMAT)
        self.assertEqual(result['cases_passed'], 15)
        self.assertEqual(len(result['cases']), 15)
        self.assertTrue(all(v['python_rejected'] and v['node_rejected']
                            for v in result['cases']))
        self.assertFalse(result['independent_devices_proven'])
        self.assertFalse(result['external_retention_proven'])
        self.assertFalse(result['mainnet_active'])
        self.assertFalse(result['economic_activation'])

    def test_wrong_external_anchor_refused(self):
        with self.assertRaises(ValueError):
            campaign.run(str(self.base.trust), str(self.path), '0' * 64)

    def test_mutations_do_not_touch_original_capsule(self):
        before = self.path.read_bytes()
        mutated = campaign.adversaries(before)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(mutated), 15)
        self.assertTrue(all(v != before for _, v in mutated))

    def test_node_crash_cannot_masquerade_as_safe_rejection(self):
        safe_baseline = {'dual': {'python_verified': True, 'node_verified': True}}
        with mock.patch.object(campaign.gate4, 'build', return_value=safe_baseline), \
             mock.patch.object(campaign.subprocess, 'run') as fake:
            fake.return_value.returncode = 1
            fake.return_value.stderr = b'node: fatal error'
            fake.return_value.stdout = b''
            with self.assertRaisesRegex(ValueError, 'VERIFIER DISAGREEMENT'):
                campaign.run(str(self.base.trust), str(self.path), self.digest)


if __name__ == '__main__':
    unittest.main()
