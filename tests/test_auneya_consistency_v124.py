"""Adversarial cross-runtime Merkle prefix consistency regression (v1.24)."""
import copy
import hashlib
import os
from unittest.mock import patch
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


class BoundedInputTests(unittest.TestCase):
    def test_both_merkle_clis_reject_nonregular_and_oversized_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            record = {'chain_id': 'io-test', 'sequence_decimal': '1',
                      **{k: hashlib.sha256(k.encode()).hexdigest()
                         for k in tr.KEYS[2:]}}
            state = {'format': tr.FORMAT, 'entries': [record],
                     'root_sha256': tr.leaf(record)}
            root = state['root_sha256']

            for version, proof, limit, py_action, pins in (
                ('transparency_v123', tr.prove(state, 0), tr.MAX_JOURNAL,
                 'verify-proof', ['--expected-root', root, '--expected-size', '1']),
                ('consistency_v124', ct.generate(state, 1, root), 4096,
                 'verify', ['--expected-old-root', root, '--expected-new-root', root,
                            '--expected-old-size', '1', '--expected-new-size', '1']),
            ):
                with self.subTest(version=version):
                    case = d / version
                    case.mkdir(mode=0o700)

                    valid = case / 'valid.json'
                    tr.atomic_write(valid, tr.canonical(proof), False)

                    link = case / 'link.json'
                    link.symlink_to(valid)

                    fifo = case / 'fifo'
                    os.mkfifo(fifo, 0o600)

                    large = case / 'large.json'
                    with large.open('wb') as f:
                        f.truncate(limit + 1)

                    original = case / 'original.json'
                    original.write_bytes(tr.canonical(proof))

                    hard = case / 'hard.json'

                    # Android Python may omit os.link entirely.
                    # Node.js provides an independent link syscall binding.
                    link_script = (
                        "const fs=require('fs');"
                        "try{fs.linkSync(process.argv[1],process.argv[2]);}"
                        "catch(e){if(['ENOSYS','ENOTSUP','EOPNOTSUPP',"
                        "'EPERM','EACCES','EXDEV'].includes(e.code)){"
                        "console.error(e.code);process.exit(77)}throw e}"
                    )

                    link_result = subprocess.run(
                        ['node', '-e', link_script, str(original), str(hard)],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    bad_inputs = [link, fifo, large, case]

                    if link_result.returncode == 0:
                        self.assertEqual(original.stat().st_nlink, 2)
                        self.assertEqual(hard.stat().st_nlink, 2)
                        bad_inputs.append(hard)
                    elif link_result.returncode == 77:
                        print(
                            'Real hardlink fixture unavailable: '
                            + link_result.stderr.strip()
                            + '; mandatory metadata rejection test remains active',
                            file=sys.stderr,
                        )
                    else:
                        self.fail(
                            'Unexpected hardlink fixture failure: '
                            + link_result.stderr
                        )

                    for runtime in ('python', 'node'):
                        program = ROOT / 'tools/auneya' / ('auneya_' + version +
                                  ('.py' if runtime == 'python' else '.js'))

                        cmd = ([sys.executable, str(program), py_action]
                               if runtime == 'python' else ['node', str(program)])

                        good = subprocess.run(
                            cmd + ['--proof', str(valid)] + pins,
                            capture_output=True,
                            timeout=10,
                        )

                        self.assertEqual(good.returncode, 0, good.stderr)

                        for bad in bad_inputs:
                            with self.subTest(runtime=runtime, bad=bad.name):
                                result = subprocess.run(
                                    cmd + ['--proof', str(bad)] + pins,
                                    capture_output=True,
                                    timeout=10,
                                )

                                self.assertNotEqual(result.returncode, 0)
                                self.assertEqual(result.stdout, b'')
                                self.assertIn(b'REJECTED:', result.stderr)

    def test_simulated_hardlink_metadata_rejected(self):
        # Mandatory on every supported platform, including Android.
        # Test the actual readers, not a duplicate validation function.
        from types import SimpleNamespace

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'regular.json'
            p.write_bytes(tr.canonical({'data': 'valid'}))

            self.assertEqual(tr.safe_read(p), {'data': 'valid'})

            actual = p.stat()

            simulated = SimpleNamespace(
                st_mode=actual.st_mode,
                st_nlink=2,
            )

            with patch.object(tr.os, 'fstat', return_value=simulated):
                with self.assertRaisesRegex(ValueError, 'bounded regular'):
                    tr.safe_read(p)

            script = (
                "const fs=require('fs');"
                "const read=require(process.argv[1]);"
                "const original=fs.fstatSync;"
                "let seen=false;"
                "fs.fstatSync=(...a)=>{"
                "const s=original(...a);"
                "seen=true;s.nlink=2n;return s};"
                "try{read(process.argv[2],4096);process.exit(2)}"
                "catch(e){"
                "if(!seen||!e.message.includes('not a bounded regular file'))"
                "process.exit(3)}"
            )

            result = subprocess.run(
                ['node', '-e', script,
                 str(ROOT / 'tools/auneya/auneya_bounded_input.js'),
                 str(p)],
                capture_output=True,
                timeout=10,
            )

            self.assertEqual(result.returncode, 0, result.stderr)


    def test_python_input_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'data.json'
            p.write_bytes(tr.canonical({'data': 'x' * 4096}))

            with self.assertRaisesRegex(ValueError, 'bounded regular'):
                tr.safe_read(p, max_bytes=4096)

            self.assertEqual(tr.safe_read(p)['data'], 'x' * 4096)

    def test_detect_growth_during_descriptor_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'data.json'
            p.write_bytes(tr.canonical({'data': 'unchanged'}))
            original_read = os.read
            changed = False

            def grow_then_read(fd, amount):
                nonlocal changed
                if not changed:
                    changed = True
                    with p.open('ab') as out:
                        out.write(b' ')
                return original_read(fd, amount)

            with patch.object(tr.os, 'read', side_effect=grow_then_read):
                with self.assertRaisesRegex(ValueError, 'concurrent input mutation'):
                    tr.safe_read(p)

            p.write_bytes(tr.canonical({'data': 'unchanged'}))

            script = (
                "const fs=require('fs');const read=require(process.argv[1]);"
                "const path=process.argv[2];const original=fs.readSync;"
                "let changed=false;fs.readFileSync=()=>{throw Error('path reread')};"
                "fs.readSync=(...a)=>{if(!changed){changed=true;"
                "fs.appendFileSync(path,' ');}return original(...a)};"
                "try{read(path,4096);process.exit(2)}catch(e){"
                "if(!changed||!e.message.includes('concurrent input mutation'))"
                "process.exit(3)}"
            )

            result = subprocess.run(
                ['node', '-e', script,
                 str(ROOT / 'tools/auneya/auneya_bounded_input.js'),
                 str(p)],
                capture_output=True,
                timeout=10,
            )

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
