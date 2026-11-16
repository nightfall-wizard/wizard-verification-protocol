"""Real Ed25519 quorum and ACK verification; simulated local fixture only."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT / 'tools/auneya')]
import auneya_fieldtrial_v122 as trial
import auneya_peer_gate_v16 as canonical
import test_auneya_gate3_receipt_v113 as prior


class FieldTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = prior.Gate3AcceptanceTests(
            'test_signed_acceptance_and_verification')
        try:
            cls.fx.setUp()
            cls.fx.issue()
            cls.paths = {
                'trust': cls.fx.fx.fx.trust,
                'capsule': cls.fx.fx.path,
                'ack': cls.fx.path,
                'floor': cls.fx.fx.floor,
                'recipient_public': cls.fx.public,
            }
            cls.original = {
                key: Path(path).read_bytes() for key, path in cls.paths.items()
            }
        except BaseException:
            cls.fx.doCleanups()
            raise

    @classmethod
    def tearDownClass(cls):
        try:
            cls.fx.doCleanups()
        finally:
            super().tearDownClass()

    def setUp(self):
        for key, path in self.paths.items():
            Path(path).write_bytes(self.original[key])
            Path(path).chmod(0o600)
        self.params = {key: str(path) for key, path in self.paths.items()}
        self.params.update({
            'recipient_pin': self.fx.pin,
            **{'expected_' + key: hashlib.sha256(self.original[key]).hexdigest()
               for key in ('trust', 'capsule', 'ack', 'floor')}
        })

    def build(self, **changes):
        return trial.run(SimpleNamespace(**(self.params | changes)))

    def test_genuine_dual_runtime_artifacts(self):
        a, b = self.build(), self.build()
        self.assertEqual(a, b)
        self.assertTrue(a['python_ack_verified'] and a['node_ack_verified'])
        self.assertTrue(a['python_quorum_verified'] and a['node_quorum_verified'])
        self.assertFalse(a['independent_devices_proven'])
        self.assertFalse(a['external_retention_proven'])
        self.assertFalse(a['real_rollback_experiment_proven'])

    def test_reject_all_wrong_external_commitments(self):
        for key in ('expected_trust', 'expected_capsule',
                    'expected_ack', 'expected_floor', 'recipient_pin'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.build(**{key: 'f' * 64 if self.params[key] != 'f' * 64
                                 else 'e' * 64})

    def test_forged_ack_rejected_even_with_new_digest(self):
        path = Path(self.paths['ack'])
        obj = json.loads(path.read_bytes())
        obj['body']['chain_id'] = 'forged-research-chain'
        forged = canonical.canonical(obj) + b'\n'
        path.write_bytes(forged)
        with self.assertRaises(ValueError):
            self.build(expected_ack=hashlib.sha256(forged).hexdigest())

    def test_modified_floor_rejected_even_with_new_digest(self):
        path = Path(self.paths['floor'])
        obj = json.loads(path.read_bytes())
        obj['sequence'] += 1
        forged = canonical.canonical(obj) + b'\n'
        path.write_bytes(forged)
        with self.assertRaises(ValueError):
            self.build(expected_floor=hashlib.sha256(forged).hexdigest())

    def test_missing_external_hash_rejected(self):
        with self.assertRaises(ValueError):
            self.build(expected_ack='')

    def test_report_exclusive_and_no_input_mutation(self):
        out = self.fx.fx.fx.root / 'fieldtrial-v122-report.json'
        out.unlink(missing_ok=True)
        cmd = [sys.executable, str(ROOT / 'tools/auneya/auneya_fieldtrial_v122.py')]
        for key, value in self.params.items():
            cmd += ['--' + key.replace('_', '-'), str(value)]
        cmd += ['--report', str(out)]
        a = subprocess.run(cmd, capture_output=True, timeout=120)
        self.assertEqual(a.returncode, 0, a.stderr.decode())
        self.assertEqual(a.stdout, out.read_bytes())
        self.assertEqual(out.stat().st_mode & 0o777, 0o600)
        b = subprocess.run(cmd, capture_output=True, timeout=120)
        self.assertNotEqual(b.returncode, 0)
        for key, path in self.paths.items():
            self.assertEqual(Path(path).read_bytes(), self.original[key])
