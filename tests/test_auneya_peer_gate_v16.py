"""
AUNEYA v1.6 adversarial regression suite.

Real Ed25519 signatures.
Bounded binary frames.
Persistent SQLite replay protection.
"""

import base64
import copy
import json
import os

from pathlib import Path

import sqlite3
import struct
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


GENERATE = '''
const c=require('node:crypto');

const k=c.generateKeyPairSync('ed25519');

process.stdout.write(JSON.stringify({
  private:k.privateKey.export({
    type:'pkcs8',
    format:'pem'
  }),
  public:k.publicKey.export({
    type:'spki',
    format:'pem'
  })
}));
'''


SIGN = '''
const c=require('node:crypto');

let a=[];

process.stdin.on('data',x=>a.push(x));

process.stdin.on('end',()=>{

  const x=JSON.parse(
    Buffer.concat(a).toString()
  );

  const b=Buffer.from(
    x.payload,
    'base64'
  );

  process.stdout.write(
    c.sign(
      null,
      Buffer.concat([
        Buffer.concat([Buffer.from('AUNEYA/WVP:PEER:V1.6', 'ascii'), Buffer.from([0])]),
        b
      ]),
      c.createPrivateKey(x.private)
    ).toString('base64')
  );
});
'''


class PeerGateTests(unittest.TestCase):

    def setUp(self):

        self.tmp = tempfile.TemporaryDirectory(
            prefix='auneya-v16-'
        )

        self.addCleanup(
            self.tmp.cleanup
        )

        self.base = Path(
            self.tmp.name
        )

        keys = json.loads(
            subprocess.check_output(
                [
                    'node',
                    '-e',
                    GENERATE
                ]
            )
        )

        self.private = keys['private']

        self.key = (
            self.base /
            'peer-public.pem'
        )

        self.key.write_text(
            keys['public']
        )

        self.key.chmod(
            0o600
        )

        self.key_hash = gate.sha(
            self.key.read_bytes()
        )

        self.frame = (
            self.base /
            'frame.bin'
        )

        self.ledger = (
            self.base /
            'gate.sqlite'
        )

        self.now = 1780000000

        self.obj = {

            'format':
                gate.FORMAT,

            'chain_id':
                'auneya-research-v1',

            'sender':
                'phone-alpha',

            'epoch':
                1,

            'counter':
                1,

            'issued_at':
                self.now - 3,

            'expires_at':
                self.now + 40,

            'challenge_sha256':
                '1' * 64,

            'manifest_sha256':
                '2' * 64,

            'checkpoint_sha256':
                '3' * 64,

            'public_key_sha256':
                self.key_hash
        }

        self.write(
            self.obj
        )

    def write(
        self,
        o,
        valid=True
    ):

        obj = copy.deepcopy(o)

        signed = gate.canonical(
            obj
        )

        request = json.dumps({

            'private':
                self.private,

            'payload':
                base64.b64encode(
                    signed
                ).decode()
        })

        sig = subprocess.check_output(
            [
                'node',
                '-e',
                SIGN
            ],
            input=request.encode()
        ).decode()

        obj['signature_b64'] = (
            sig
            if valid
            else
            base64.b64encode(
                bytes(64)
            ).decode()
        )

        body = gate.canonical(
            obj
        )

        self.frame.write_bytes(
            struct.pack(
                '>I',
                len(body)
            ) +
            body
        )

        self.frame.chmod(
            0o600
        )

    def run_gate(
        self,
        action='accept',
        **kw
    ):

        o = dict(

            frame=self.frame,

            key=self.key,

            key_hash=self.key_hash,

            sender='phone-alpha',

            chain_id='auneya-research-v1',

            pin=self.obj[
                'checkpoint_sha256'
            ],

            challenge=self.obj[
                'challenge_sha256'
            ],

            manifest=self.obj[
                'manifest_sha256'
            ],

            ledger=self.ledger,

            now=self.now
        )

        o.update(kw)

        return gate.handle(
            action,
            **o
        )

    def test_valid_ed25519_and_durable_replay(self):

        x = self.run_gate()

        self.assertTrue(
            x['replay_persisted']
        )

        with self.assertRaisesRegex(
            gate.GateError,
            'REPLAY|noncontiguous'
        ):

            self.run_gate()

        with sqlite3.connect(
            self.ledger
        ) as db:

            self.assertEqual(
                db.execute(
                    'SELECT COUNT(*) FROM messages'
                ).fetchone()[0],
                1
            )

    def test_verification_only_does_not_consume(self):

        self.assertFalse(
            self.run_gate(
                'verify'
            )['replay_persisted']
        )

        self.run_gate()

    def test_forgery_does_not_consume(self):

        self.write(
            self.obj,
            valid=False
        )

        with self.assertRaisesRegex(
            gate.GateError,
            'signature rejected'
        ):

            self.run_gate()

        self.write(
            self.obj
        )

        self.run_gate()

    def test_reject_changed_signed_payload(self):

        raw = self.frame.read_bytes()

        obj = gate.decode_frame(
            raw
        )

        obj['epoch'] = 2

        body = gate.canonical(
            obj
        )

        self.frame.write_bytes(
            struct.pack(
                '>I',
                len(body)
            ) +
            body
        )

        with self.assertRaisesRegex(
            gate.GateError,
            'signature rejected'
        ):

            self.run_gate()

    def test_wrong_peer_network_and_key_pins(self):

        for kw in (
            {
                'sender': 'wrong'
            },
            {
                'chain_id': 'wrong'
            },
            {
                'key_hash': '0' * 64
            },
            {
                'pin': '0' * 64
            }
        ):

            with self.subTest(kw=kw):

                with self.assertRaises(
                    gate.GateError
                ):

                    self.run_gate(
                        **kw
                    )

    def test_frame_truncation_and_extra_bytes(self):

        good = self.frame.read_bytes()

        for bad in (
            good[:-1],
            good + b'X',
            b'\0\0\0\0',
            good[:3]
        ):

            with self.subTest(
                bad=bad[:5]
            ):

                self.frame.write_bytes(
                    bad
                )

                with self.assertRaises(
                    gate.GateError
                ):

                    self.run_gate()

        self.frame.write_bytes(
            good
        )

    def test_duplicate_json_key_and_noncanonical_json(self):

        obj = gate.decode_frame(
            self.frame.read_bytes()
        )

        body = gate.canonical(
            obj
        ).replace(
            b'"epoch":1',
            b'"epoch":1,"epoch":1'
        )

        self.frame.write_bytes(
            struct.pack(
                '>I',
                len(body)
            ) +
            body
        )

        with self.assertRaisesRegex(
            gate.GateError,
            'duplicate JSON'
        ):

            self.run_gate()

    def test_maximum_resource_budget(self):

        self.frame.write_bytes(
            struct.pack(
                '>I',
                65537
            ) +
            b'x' * 65537
        )

        with self.assertRaises(
            gate.GateError
        ):

            self.run_gate()

    def test_expiry(self):

        with self.assertRaisesRegex(
            gate.GateError,
            'time window'
        ):

            self.run_gate(
                now=self.now + 999
            )

    def test_counter_epoch_and_reused_anchor(self):

        self.run_gate()

        wrong = dict(
            self.obj,
            counter=3,
            challenge_sha256='4' * 64,
            manifest_sha256='5' * 64
        )

        self.write(
            wrong
        )

        with self.assertRaisesRegex(
            gate.GateError,
            'noncontiguous'
        ):

            self.run_gate(
                challenge=wrong[
                    'challenge_sha256'
                ],
                manifest=wrong[
                    'manifest_sha256'
                ]
            )

        good = dict(
            wrong,
            counter=2
        )

        self.write(
            good
        )

        self.run_gate(
            challenge=good[
                'challenge_sha256'
            ],
            manifest=good[
                'manifest_sha256'
            ]
        )

        repeated = dict(
            self.obj,
            counter=3
        )

        self.write(
            repeated
        )

        with self.assertRaisesRegex(
            gate.GateError,
            'REPLAY'
        ):

            self.run_gate()

        next_epoch = dict(
            self.obj,
            epoch=2,
            counter=1,
            challenge_sha256='6' * 64,
            manifest_sha256='7' * 64
        )

        self.write(
            next_epoch
        )

        self.run_gate(
            challenge=next_epoch[
                'challenge_sha256'
            ],
            manifest=next_epoch[
                'manifest_sha256'
            ]
        )

    def test_clock_rollback_does_not_consume(self):

        self.run_gate()

        later = dict(
            self.obj,
            counter=2,
            challenge_sha256='4' * 64,
            manifest_sha256='5' * 64
        )

        self.write(
            later
        )

        with self.assertRaisesRegex(
            gate.GateError,
            'clock rollback'
        ):

            self.run_gate(
                challenge=later[
                    'challenge_sha256'
                ],
                manifest=later[
                    'manifest_sha256'
                ],
                now=self.now - 1
            )

        self.run_gate(
            challenge=later[
                'challenge_sha256'
            ],
            manifest=later[
                'manifest_sha256'
            ]
        )

    def test_transaction_rollback_on_insert_failure(self):

        self.run_gate()

        with sqlite3.connect(
            self.ledger
        ) as db:

            db.execute(
                'CREATE TRIGGER broken '
                'BEFORE INSERT ON messages '
                "BEGIN SELECT RAISE(ABORT,'failure'); END;"
            )

        later = dict(
            self.obj,
            counter=2,
            challenge_sha256='4' * 64,
            manifest_sha256='5' * 64
        )

        self.write(
            later
        )

        with self.assertRaises(
            gate.GateError
        ):

            self.run_gate(
                challenge=later[
                    'challenge_sha256'
                ],
                manifest=later[
                    'manifest_sha256'
                ]
            )

        with sqlite3.connect(
            self.ledger
        ) as db:

            self.assertEqual(
                db.execute(
                    'SELECT COUNT(*) FROM messages'
                ).fetchone()[0],
                1
            )

            self.assertEqual(
                db.execute(
                    'SELECT last_counter FROM peers'
                ).fetchone()[0],
                1
            )

    def test_private_file_and_symlink_rejection(self):

        self.frame.chmod(
            0o644
        )

        with self.assertRaises(
            gate.GateError
        ):

            self.run_gate()

        self.frame.chmod(
            0o600
        )

        link = (
            self.base /
            'link'
        )

        link.symlink_to(
            self.frame
        )

        with self.assertRaises(
            OSError
        ):

            self.run_gate(
                frame=link
            )


if __name__ == '__main__':
    unittest.main()
