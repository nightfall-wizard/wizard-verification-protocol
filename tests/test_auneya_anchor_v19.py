"""
Adversarial Gate 3 offline
signed-checkpoint conformance.
"""

import json

from pathlib import Path

import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(
    __file__
).resolve().parents[1]

sys.path.insert(
    0,
    str(
        ROOT /
        'tools' /
        'auneya'
    )
)

import auneya_peer_gate_v16 as gate
import auneya_anchor_v19 as v19


KEYGEN = """
const c=require('node:crypto');

const k=c.generateKeyPairSync('ed25519');

console.log(JSON.stringify({
    priv:k.privateKey.export({
        type:'pkcs8',
        format:'pem'
    }),

    pub:k.publicKey.export({
        type:'spki',
        format:'pem'
    })
}));
"""


class AnchorTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory(
            prefix='auneya-v19-'
        )

        self.addCleanup(
            temp.cleanup
        )

        self.root = Path(
            temp.name
        )

        self.root.chmod(
            0o700
        )

        self.db = (
            self.root /
            'replay.sqlite'
        )

        self.prv = (
            self.root /
            'signer-private.pem'
        )

        self.pub = (
            self.root /
            'signer-public.pem'
        )

        keys = json.loads(
            subprocess.check_output(
                [
                    'node',
                    '-e',
                    KEYGEN
                ]
            )
        )

        for path, value in (
            (
                self.prv,
                keys['priv']
            ),
            (
                self.pub,
                keys['pub']
            )
        ):
            path.write_text(
                value
            )

            path.chmod(
                0o600
            )

        self.pin = gate.sha(
            self.pub.read_bytes()
        )

        self.chain = (
            'auneya-research-v1'
        )

        self.put(1)


    def put(self, n):
        gate.commit(
            self.db,

            {
                'chain_id':
                    self.chain,

                'sender':
                    'phone-alpha',

                'epoch':
                    1,

                'counter':
                    n,

                'challenge_sha256':
                    f'{n:064x}',

                'manifest_sha256':
                    f'{n+100:064x}'
            },

            1000 + n
        )


    def snap(
        self,
        name,
        previous=None
    ):
        target = (
            self.root /
            name
        )

        result = v19.capture(
            self.db,
            target,
            self.prv,
            self.pub,
            self.pin,
            self.chain,
            previous
        )

        self.assertEqual(
            result['status'],
            'EXACT_SIGNED_SNAPSHOT_MATCH'
        )

        return target


    def test_signed_baseline_and_no_false_external_claim(
        self
    ):
        anchor = self.snap(
            'first.json'
        )

        result = v19.verify(
            self.db,
            anchor,
            self.pub,
            self.pin
        )

        self.assertEqual(
            result['sequence'],
            1
        )

        self.assertFalse(
            result['externally_retained_proven']
        )


    def test_append_only_hash_chain(self):
        first = self.snap(
            'first.json'
        )

        self.put(2)

        second = self.snap(
            'second.json',
            first
        )

        result = v19.verify(
            self.db,
            second,
            self.pub,
            self.pin,
            first
        )

        self.assertEqual(
            result['sequence'],
            2
        )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'ROLLBACK_OR_TAMPER'
        ):
            v19.verify(
                self.db,
                first,
                self.pub,
                self.pin
            )


    def test_new_sender_before_prior_sort_order(
        self
    ):
        first = self.snap(
            'first.json'
        )

        gate.commit(
            self.db,

            {
                'chain_id':
                    self.chain,

                'sender':
                    'aa-new-phone',

                'epoch':
                    1,

                'counter':
                    1,

                'challenge_sha256':
                    'a' * 64,

                'manifest_sha256':
                    'b' * 64
            },

            1002
        )

        second = self.snap(
            'second.json',
            first
        )

        result = v19.verify(
            self.db,
            second,
            self.pub,
            self.pin,
            first
        )

        self.assertEqual(
            result['message_count'],
            2
        )


    def test_restored_old_sqlite_rejected(self):
        first = self.snap(
            'first.json'
        )

        old = (
            self.root /
            'old-backup.sqlite'
        )

        shutil.copyfile(
            self.db,
            old
        )

        self.put(2)

        second = self.snap(
            'second.json',
            first
        )

        shutil.copyfile(
            old,
            self.db
        )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'ROLLBACK_OR_TAMPER'
        ):
            v19.verify(
                self.db,
                second,
                self.pub,
                self.pin,
                first
            )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'rollback'
        ):
            self.snap(
                'third.json',
                second
            )


    def test_history_rewrite_and_wrong_pin_rejected(
        self
    ):
        anchor = self.snap(
            'first.json'
        )

        with sqlite3.connect(
            self.db
        ) as db:
            db.execute(
                'UPDATE messages '
                'SET challenge_sha256=?',

                (
                    'e' * 64,
                )
            )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'ROLLBACK_OR_TAMPER'
        ):
            v19.verify(
                self.db,
                anchor,
                self.pub,
                self.pin
            )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'pin mismatch'
        ):
            v19.verify(
                self.db,
                anchor,
                self.pub,
                'b' * 64
            )


    def test_forged_anchor_and_tampered_signature_rejected(
        self
    ):
        first = self.snap(
            'first.json'
        )

        obj = json.loads(
            first.read_text()
        )

        obj['body']['message_count'] += 1

        corrupted = (
            self.root /
            'corrupted.json'
        )

        corrupted.write_bytes(
            gate.canonical(obj) +
            b'\n'
        )

        corrupted.chmod(
            0o600
        )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'signature rejected'
        ):
            v19.verify(
                self.db,
                corrupted,
                self.pub,
                self.pin
            )


    def test_noncanonical_anchor_and_path_collision(
        self
    ):
        first = self.snap(
            'first.json'
        )

        with self.assertRaises(
            FileExistsError
        ):
            self.snap(
                'first.json'
            )

        bad = (
            self.root /
            'duplicate.json'
        )

        raw = first.read_bytes().replace(
            b'"sequence":1',
            b'"sequence":1,"sequence":1'
        )

        bad.write_bytes(raw)

        bad.chmod(
            0o600
        )

        with self.assertRaises(
            ValueError
        ):
            v19.verify(
                self.db,
                bad,
                self.pub,
                self.pin
            )


    def test_monotonic_history_and_missing_prefix_rejected(
        self
    ):
        first = self.snap(
            'first.json'
        )

        self.put(2)

        with sqlite3.connect(
            self.db
        ) as db:
            db.execute(
                'DELETE FROM messages '
                'WHERE counter=1'
            )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'missing initial|gap'
        ):
            self.snap(
                'invalid.json',
                first
            )


    def test_wrong_chain_and_untrusted_key_rejected(
        self
    ):
        first = self.snap(
            'first.json'
        )

        self.put(2)

        obj = json.loads(
            first.read_text()
        )

        obj['body']['chain_id'] = (
            'other-research-chain'
        )

        wrong = (
            self.root /
            'wrong.json'
        )

        wrong.write_bytes(
            gate.canonical(obj) +
            b'\n'
        )

        wrong.chmod(
            0o600
        )

        with self.assertRaisesRegex(
            v19.AnchorError,
            'signature rejected'
        ):
            self.snap(
                'invalid.json',
                wrong
            )


if __name__ == '__main__':
    unittest.main()
