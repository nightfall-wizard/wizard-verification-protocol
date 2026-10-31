"""
Adversarial Gate 3 high-water tests.

Two isolated local stores.
No real physical-device independence claim.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / 'tools' / 'auneya')
)

import auneya_peer_gate_v16 as gate
import auneya_anchor_v19 as v19
import auneya_witness_v110 as v110


KEYS = """
const c=require('node:crypto');

const k=c.generateKeyPairSync('ed25519');

console.log(JSON.stringify({
 priv:k.privateKey.export({
  format:'pem',
  type:'pkcs8'
 }),
 pub:k.publicKey.export({
  format:'pem',
  type:'spki'
 })
}));
"""


class IndependentKeeperTests(unittest.TestCase):

    def setUp(self):

        tmp = tempfile.TemporaryDirectory(
            prefix='auneya-v110-'
        )

        self.addCleanup(
            tmp.cleanup
        )

        self.d = Path(tmp.name)

        self.d.chmod(
            0o700
        )

        self.producer = self.d / 'producer'
        self.keeper = self.d / 'keeper'

        for p in (
            self.producer,
            self.keeper
        ):

            p.mkdir(
                mode=0o700
            )

        self.db = (
            self.producer /
            'replay.sqlite'
        )

        self.store = (
            self.keeper /
            'keeper.sqlite'
        )

        self.chain = 'auneya-research-v1'

        (
            self.a_priv,
            self.a_pub,
            self.a_pin
        ) = self.keys(
            self.producer,
            'anchor'
        )

        (
            self.w_priv,
            self.w_pub,
            self.w_pin
        ) = self.keys(
            self.keeper,
            'witness'
        )

        self.commit(1)


    def keys(self, parent, name):

        obj = json.loads(
            subprocess.check_output(
                [
                    'node',
                    '-e',
                    KEYS
                ]
            )
        )

        prv = (
            parent /
            (name + '-private.pem')
        )

        pub = (
            parent /
            (name + '-public.pem')
        )

        for path, value in (
            (prv, obj['priv']),
            (pub, obj['pub'])
        ):

            path.write_text(
                value
            )

            path.chmod(
                0o600
            )

        return (
            prv,
            pub,
            gate.sha(pub.read_bytes())
        )


    def commit(self, n):

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


    def checkpoint(self, seq, prev=None):

        target = (
            self.producer /
            f'anchor-{seq}.json'
        )

        v19.capture(
            self.db,
            target,
            self.a_priv,
            self.a_pub,
            self.a_pin,
            self.chain,
            prev
        )

        return target


    def witness(
        self,
        checkpoint,
        seq,
        prev=None
    ):

        dest = (
            self.keeper /
            f'ack-{seq}.json'
        )

        result = v110.accept(
            self.store,
            checkpoint,
            self.a_pub,
            self.a_pin,
            self.w_priv,
            self.w_pub,
            self.w_pin,
            dest,
            prev
        )

        self.assertFalse(
            result['independent_device_proven']
        )

        self.assertFalse(
            result['externally_retained_proven']
        )

        return dest


    def test_independent_signature_chain_and_forward_growth(
        self
    ):

        a1 = self.checkpoint(1)
        r1 = self.witness(a1, 1)

        self.commit(2)

        a2 = self.checkpoint(
            2,
            a1
        )

        r2 = self.witness(
            a2,
            2,
            r1
        )

        out = v110.verify(
            a2,
            r2,
            self.a_pub,
            self.a_pin,
            self.w_pub,
            self.w_pin,
            r1
        )

        self.assertEqual(
            out['sequence'],
            2
        )

        body = v110.inspect_receipt(
            r2,
            self.w_pub.read_bytes(),
            self.w_pin
        )[0]

        self.assertEqual(
            body['previous_receipt_sha256'],
            gate.sha(r1.read_bytes())
        )


    def test_old_db_restore_rejected_by_outside_highwater(
        self
    ):

        a1 = self.checkpoint(1)
        r1 = self.witness(a1, 1)

        backup = (
            self.d /
            'keeper-backup.sqlite'
        )

        shutil.copyfile(
            self.store,
            backup
        )

        self.commit(2)

        a2 = self.checkpoint(
            2,
            a1
        )

        r2 = self.witness(
            a2,
            2,
            r1
        )

        shutil.copyfile(
            backup,
            self.store
        )

        self.commit(3)

        a3 = self.checkpoint(
            3,
            a2
        )

        with self.assertRaisesRegex(
            v110.WitnessError,
            'high-water'
        ):

            self.witness(
                a3,
                3,
                r2
            )


    def test_skip_previous_receipt_rejected(self):

        a1 = self.checkpoint(1)

        self.witness(
            a1,
            1
        )

        self.commit(2)

        a2 = self.checkpoint(
            2,
            a1
        )

        with self.assertRaisesRegex(
            v110.WitnessError,
            'high-water'
        ):

            self.witness(
                a2,
                2
            )


    def test_unsigned_and_modified_receipts_rejected(
        self
    ):

        a1 = self.checkpoint(1)
        r1 = self.witness(a1, 1)

        raw = r1.read_bytes()

        bad = (
            self.keeper /
            'forged.json'
        )

        bad.write_bytes(
            raw.replace(
                b'"sequence":1',
                b'"sequence":2'
            )
        )

        bad.chmod(
            0o600
        )

        with self.assertRaises(
            ValueError
        ):

            v110.verify(
                a1,
                bad,
                self.a_pub,
                self.a_pin,
                self.w_pub,
                self.w_pin
            )

        with self.assertRaisesRegex(
            ValueError,
            'pin mismatch'
        ):

            v110.verify(
                a1,
                r1,
                self.a_pub,
                self.a_pin,
                self.w_pub,
                'a' * 64
            )


    def test_tampered_anchor_rejected(self):

        a1 = self.checkpoint(1)

        obj = json.loads(
            a1.read_text()
        )

        obj['body']['message_count'] += 1

        forged = (
            self.producer /
            'forged.json'
        )

        forged.write_bytes(
            gate.canonical(obj) +
            b'\n'
        )

        forged.chmod(
            0o600
        )

        with self.assertRaises(
            ValueError
        ):

            self.witness(
                forged,
                1
            )


    def test_duplicate_output_no_overwrite_no_store_advance(
        self
    ):

        a1 = self.checkpoint(1)
        r1 = self.witness(a1, 1)

        self.commit(2)

        a2 = self.checkpoint(
            2,
            a1
        )

        with self.assertRaisesRegex(
            ValueError,
            'already exists'
        ):

            v110.accept(
                self.store,
                a2,
                self.a_pub,
                self.a_pin,
                self.w_priv,
                self.w_pub,
                self.w_pin,
                r1,
                r1
            )

        body = v110.inspect_receipt(
            r1,
            self.w_pub.read_bytes(),
            self.w_pin
        )[0]

        self.assertEqual(
            body['sequence'],
            1
        )

        self.witness(
            a2,
            2,
            r1
        )


    def test_forged_witness_private_rejected_without_state_change(
        self
    ):

        a1 = self.checkpoint(1)

        bad_private, _, _ = self.keys(
            self.keeper,
            'attacker'
        )

        with self.assertRaisesRegex(
            ValueError,
            'key pair mismatch'
        ):

            v110.accept(
                self.store,
                a1,
                self.a_pub,
                self.a_pin,
                bad_private,
                self.w_pub,
                self.w_pin,
                self.keeper / 'no.json'
            )

        self.witness(
            a1,
            1
        )


    def test_export_recovery_rejects_rolled_back_floor(
        self
    ):

        a1 = self.checkpoint(1)
        r1 = self.witness(a1, 1)

        r1export = (
            self.keeper /
            'export-1.json'
        )

        out = v110.export_receipt(
            self.store,
            self.chain,
            self.w_pub,
            self.w_pin,
            r1export,
            r1
        )

        self.assertEqual(
            out['sequence'],
            1
        )

        self.assertEqual(
            r1.read_bytes(),
            r1export.read_bytes()
        )

        backup = (
            self.d /
            'old.sqlite'
        )

        shutil.copyfile(
            self.store,
            backup
        )

        self.commit(2)

        a2 = self.checkpoint(
            2,
            a1
        )

        r2 = self.witness(
            a2,
            2,
            r1
        )

        shutil.copyfile(
            backup,
            self.store
        )

        with self.assertRaisesRegex(
            ValueError,
            'below outside receipt floor'
        ):

            v110.export_receipt(
                self.store,
                self.chain,
                self.w_pub,
                self.w_pin,
                self.keeper / 'invalid.json',
                r2
            )


    def test_out_of_order_checkpoint_rejected(self):

        a1 = self.checkpoint(1)
        r1 = self.witness(a1, 1)

        with self.assertRaisesRegex(
            ValueError,
            'noncontiguous'
        ):

            v110.accept(
                self.store,
                a1,
                self.a_pub,
                self.a_pin,
                self.w_priv,
                self.w_pub,
                self.w_pin,
                self.keeper / 'duplicate.json',
                r1
            )


if __name__ == '__main__':
    unittest.main()
