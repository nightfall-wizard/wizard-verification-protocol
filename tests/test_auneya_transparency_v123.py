"""AUNEYA v1.23 adversarial and real-v1.22 integration tests."""

import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(ROOT / 'tools/auneya')
)

import auneya_transparency_v123 as tr


class TransparencyTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.directory = Path(self.temp.name)
        self.journal = self.directory / 'journal.json'

        tr.init(self.journal)

    def record(self, seq=1):
        return {
            **{
                k: hashlib.sha256(
                    k.encode()
                ).hexdigest()
                for k in tr.KEYS[2:]
            },
            'chain_id': 'research-chain',
            'sequence_decimal': str(seq)
        }

    def append(self, n):
        start = len(
            tr.safe_read(
                self.journal
            )['entries']
        ) + 1

        for i in range(start, n + 1):
            tr.append_record(
                self.journal,
                self.record(i)
            )

        return tr.safe_read(
            self.journal
        )

    def node_verify(self, proof, expected, size):
        file = self.directory / 'proof.json'
        file.unlink(missing_ok=True)

        tr.atomic_write(
            file,
            tr.canonical(proof),
            False
        )

        return subprocess.run(
            [
                'node',
                str(
                    ROOT /
                    'tools/auneya/auneya_transparency_v123.js'
                ),
                '--proof',
                str(file),
                '--expected-root',
                expected,
                '--expected-size',
                str(size)
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

    def test_all_tree_shapes_python_node(self):
        for n in range(1, 11):
            tr.append_record(
                self.journal,
                self.record(n)
            )

            state = tr.safe_read(
                self.journal
            )

            tr.validate(state)

            for i in range(n):
                proof = tr.prove(
                    state, i
                )

                self.assertTrue(
                    tr.verify_proof(
                        proof,
                        state['root_sha256'],
                        n
                    )
                )

                result = self.node_verify(
                    proof,
                    state['root_sha256'],
                    n
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    result.stderr
                )

                self.assertIn(
                    'INCLUDED_IN_PINNED_ROOT',
                    result.stdout
                )

    def test_strict_tamper_and_external_pins(self):
        state = self.append(5)
        proof = tr.prove(state, 2)

        variants = []

        z = copy.deepcopy(proof)
        z['record']['ack_sha256'] = 'f' * 64
        variants.append(z)

        z = copy.deepcopy(proof)
        z['index'] = 3
        variants.append(z)

        z = copy.deepcopy(proof)
        z['path'][0]['side'] = (
            'right'
            if z['path'][0]['side'] == 'left'
            else 'left'
        )
        variants.append(z)

        z = copy.deepcopy(proof)
        z['path'][0]['hash'] = 'e' * 64
        variants.append(z)

        z = copy.deepcopy(proof)
        z['path'].append({
            'side': 'left',
            'hash': 'a' * 64
        })
        variants.append(z)

        z = copy.deepcopy(proof)
        z['record']['unexpected'] = 'yes'
        variants.append(z)

        for z in variants:
            with self.subTest(z=z):
                with self.assertRaises(ValueError):
                    tr.verify_proof(
                        z,
                        state['root_sha256'],
                        5
                    )

                self.assertNotEqual(
                    self.node_verify(
                        z,
                        state['root_sha256'],
                        5
                    ).returncode,
                    0
                )

        with self.assertRaises(ValueError):
            tr.verify_proof(
                proof,
                'f' * 64,
                5
            )

        with self.assertRaises(ValueError):
            tr.verify_proof(
                proof,
                state['root_sha256'],
                4
            )

        self.assertNotEqual(
            self.node_verify(
                proof,
                'f' * 64,
                5
            ).returncode,
            0
        )

    def test_rollback_fork_and_skip_detected(self):
        old = self.append(2)
        new = self.append(3)

        result = tr.compare_history(
            old,
            new,
            old['root_sha256'],
            new['root_sha256']
        )

        self.assertEqual(
            result['status'],
            'PREFIX_CONSISTENT'
        )

        with self.assertRaisesRegex(
            ValueError, 'truncated'
        ):
            tr.compare_history(
                new,
                old,
                new['root_sha256'],
                old['root_sha256']
            )

        bad = copy.deepcopy(new)
        bad['entries'][0]['report_sha256'] = 'f' * 64

        bad['root_sha256'] = tr.root([
            tr.leaf(x)
            for x in bad['entries']
        ])

        with self.assertRaisesRegex(
            ValueError, 'fork'
        ):
            tr.compare_history(
                old,
                bad,
                old['root_sha256'],
                bad['root_sha256']
            )

        with self.assertRaisesRegex(
            ValueError, 'external'
        ):
            tr.compare_history(
                old,
                new,
                'f' * 64,
                new['root_sha256']
            )

        with self.assertRaisesRegex(
            ValueError, 'non-contiguous'
        ):
            tr.append_record(
                self.journal,
                self.record(5)
            )

    def test_noncanonical_and_symlink_refusal(self):
        self.append(1)

        good = self.journal.read_bytes()
        self.journal.write_bytes(
            good + b' '
        )

        with self.assertRaisesRegex(
            ValueError, 'noncanonical'
        ):
            tr.safe_read(self.journal)

        self.journal.write_bytes(
            good.replace(
                b'"entries":',
                b'"format":"duplicate","entries":'
            )
        )

        with self.assertRaises(ValueError):
            tr.safe_read(self.journal)

        self.journal.write_bytes(good)

        link = self.directory / 'link.json'
        link.symlink_to(self.journal)

        with self.assertRaises(ValueError):
            tr.safe_read(link)

    def test_unverified_report_refused(self):
        with self.assertRaises(ValueError):
            tr.record_from_report({
                'format':
                    'auneya-gate3-fieldtrial-offline-v1.22',
                'python_quorum_verified': True
            })

    def test_real_signed_v122_report_is_accepted(self):
        from test_auneya_fieldtrial_v122 import (
            FieldTrialTests
        )

        FieldTrialTests.setUpClass()

        try:
            fx = FieldTrialTests(
                'test_genuine_dual_runtime_artifacts'
            )

            fx.setUp()

            result = fx.build()

            rec = tr.record_from_report(
                result
            )

            self.assertEqual(
                rec['capsule_sha256'],
                result['capsule_sha256']
            )

            obj = tr.append_record(
                self.journal,
                rec
            )

            self.assertEqual(
                obj['size'],
                1
            )

        finally:
            FieldTrialTests.tearDownClass()


if __name__ == '__main__':
    unittest.main()
