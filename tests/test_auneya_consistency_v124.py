"""Adversarial cross-runtime Merkle prefix consistency regression (v1.24)."""
import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/auneya'))
import auneya_transparency_v123 as tr
import auneya_consistency_v124 as ct


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.journal = self.directory / 'journal.json'
        tr.init(self.journal)

    def record(self, sequence):
        return {
            'chain_id': 'offline-research',
            'sequence_decimal': str(sequence),
            **{key: hashlib.sha256(key.encode()).hexdigest()
               for key in tr.KEYS[2:]}
        }

    def make(self, size):
        for n in range(1, size + 1):
            tr.append_record(self.journal, self.record(n))
        return tr.safe_read(self.journal)

    def run_node(self, proof, old_root, new_root, old_size, new_size):
        path = self.directory / 'proof.json'
        path.unlink(missing_ok=True)
        tr.atomic_write(path, tr.canonical(proof), False)
        return subprocess.run([
            'node', str(ROOT / 'tools/auneya/auneya_consistency_v124.js'),
            '--proof', str(path),
            '--expected-old-root', old_root,
            '--expected-new-root', new_root,
            '--expected-old-size', str(old_size),
            '--expected-new-size', str(new_size)
        ], capture_output=True, text=True, timeout=15)

    def test_every_small_prefix_and_cross_runtime_vectors(self):
        state = self.make(33)
        leaves = tr.validate(state)
        for n in range(1, 34):
            prefix = {'format': tr.FORMAT, 'entries': state['entries'][:n],
                      'root_sha256': tr.root(leaves[:n])}
            for m in range(1, n + 1):
                old_root = tr.root(leaves[:m])
                proof = ct.generate(prefix, m, old_root)
                self.assertEqual(
                    ct.verify(proof, old_root, prefix['root_sha256'], m, n)['status'],
                    'PREFIX_CONSISTENT'
                )
                self.assertLessEqual(len(proof['path']), 9)
                if m == n or (m, n) in {
                    (1, 2), (2, 3), (3, 7), (7, 8), (8, 9),
                    (13, 32), (31, 32), (32, 33)
                }:
                    result = self.run_node(proof, old_root, prefix['root_sha256'], m, n)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('PREFIX_CONSISTENT', result.stdout)

    def test_256_entry_boundary_python_and_node(self):
        state = self.make(256)
        leaves = tr.validate(state)
        for m in (1, 2, 3, 7, 64, 127, 128, 129, 255, 256):
            old = tr.root(leaves[:m])
            proof = ct.generate(state, m, old)
            self.assertEqual(
                self.run_node(proof, old, state['root_sha256'], m, 256).returncode, 0)

    def test_tamper_fork_truncation_wrong_pins(self):
        state = self.make(9)
        original = tr.root(tr.validate(state)[:5])
        proof = ct.generate(state, 5, original)
        variants = []
        for name, value in (
            ('old_root_sha256', 'f' * 64),
            ('new_root_sha256', 'f' * 64),
            ('old_size', 4),
            ('new_size', 8),
            ('format', 'unknown')
        ):
            z = copy.deepcopy(proof)
            z[name] = value
            variants.append(z)
        for wrong_path in ([], proof['path'][:-1],
                           ['f' * 64] + proof['path'][1:],
                           proof['path'] + ['e' * 64]):
            z = copy.deepcopy(proof)
            z['path'] = wrong_path
            variants.append(z)
        z = copy.deepcopy(proof)
        z['unapproved'] = 1
        variants.append(z)
        for z in variants:
            with self.subTest(z=z):
                with self.assertRaises(ValueError):
                    ct.verify(z, original, state['root_sha256'], 5, 9)
                self.assertNotEqual(
                    self.run_node(z, original, state['root_sha256'], 5, 9).returncode, 0)
        with self.assertRaises(ValueError):
            ct.verify(proof, original, '0' * 64, 5, 9)
        # Recomputed, internally valid fork still fails against the older external pin.
        forked = copy.deepcopy(state)
        forked['entries'][1]['ack_sha256'] = 'a' * 64
        forked['root_sha256'] = tr.root([tr.leaf(x) for x in forked['entries']])
        tr.validate(forked)
        with self.assertRaises(ValueError):
            ct.generate(forked, 5, original)

    def test_same_size_and_untrusted_empty_history(self):
        state = self.make(3)
        root = state['root_sha256']
        proof = ct.generate(state, 3, root)
        self.assertEqual(proof['path'], [])
        for altered in ({**proof, 'path': ['f' * 64]},
                        {**proof, 'new_root_sha256': 'e' * 64}):
            with self.assertRaises(ValueError):
                ct.verify(altered, root, root, 3, 3)
        with self.assertRaises(ValueError):
            ct.generate(state, 0, hashlib.sha256(b'').hexdigest())

    def test_noncanonical_file_rejected_by_both_runtimes(self):
        state = self.make(2)
        old = tr.root(tr.validate(state)[:1])
        proof = ct.generate(state, 1, old)
        path = self.directory / 'proof.json'
        path.write_bytes(tr.canonical(proof) + b'\n')
        with self.assertRaises(ValueError):
            tr.safe_read(path)
        proc = subprocess.run([
            'node', str(ROOT / 'tools/auneya/auneya_consistency_v124.js'),
            '--proof', str(path), '--expected-old-root', old,
            '--expected-new-root', state['root_sha256'],
            '--expected-old-size', '1', '--expected-new-size', '2'
        ], capture_output=True, text=True, timeout=15)
        self.assertNotEqual(proc.returncode, 0)


if __name__ == '__main__':
    unittest.main()
