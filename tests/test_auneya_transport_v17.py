"""
AUNEYA v1.7 adversarial transport regression suite.

Tests real Ed25519 signatures,
localhost TCP framing,
persistent SQLite replay protection,
identity revocation and key rotation.
"""

import base64
import json
from pathlib import Path
import socket
import sqlite3
import struct
import subprocess
import sys
import tempfile
import time
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

import auneya_transport_v17 as net
import auneya_peer_gate_v16 as gate


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


SIGN = """
const c=require('node:crypto');

let b=[];

process.stdin.on(
    'data',
    x=>b.push(x)
);

process.stdin.on('end',()=>{

    let a=JSON.parse(
        Buffer.concat(b)
    );

    let s=c.sign(
        null,
        Buffer.concat([
            Buffer.from(
                'AUNEYA/WVP:PEER:V1.6\\0'
            ),
            Buffer.from(
                a.payload,
                'base64'
            )
        ]),
        c.createPrivateKey(
            a.private
        )
    );

    process.stdout.write(
        s.toString('base64')
    );
});
"""


class LoopbackTests(unittest.TestCase):

    def setUp(self):

        self.tmp = (
            tempfile.TemporaryDirectory(
                prefix='auneya-transport-v17-'
            )
        )

        self.addCleanup(
            self.tmp.cleanup
        )

        self.root = Path(
            self.tmp.name
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

        self.priv = keys['priv']

        self.key = (
            self.root /
            'peer.pem'
        )

        self.key.write_text(
            keys['pub']
        )

        self.key.chmod(
            0o600
        )

        self.pin = gate.sha(
            self.key.read_bytes()
        )

        self.policy = (
            self.root /
            'policy.json'
        )

        self.ledger = (
            self.root /
            'ledger.sqlite'
        )

        self.frame = (
            self.root /
            'message.bin'
        )

        self.ready = (
            self.root /
            'ready.json'
        )

        self.now = int(
            time.time()
        )

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
                self.now - 2,

            'expires_at':
                self.now + 75,

            'challenge_sha256':
                '1' * 64,

            'manifest_sha256':
                '2' * 64,

            'checkpoint_sha256':
                '3' * 64,

            'public_key_sha256':
                self.pin
        }

        self._enroll()

        self._frame()

    def _enroll(self):

        args = type(
            'Args',
            (),
            {
                'policy':
                    str(self.policy),

                'key':
                    str(self.key),

                'key_sha256':
                    self.pin,

                'sender':
                    'phone-alpha',

                'chain_id':
                    'auneya-research-v1',

                'checkpoint_sha256':
                    '3' * 64,

                'challenge_sha256':
                    '1' * 64,

                'manifest_sha256':
                    '2' * 64
            }
        )()

        net.enroll(
            args
        )

    def _frame(
        self,
        obj=None,
        corrupt=False
    ):

        obj = dict(
            self.obj
            if obj is None
            else obj
        )

        request = json.dumps(
            {
                'private':
                    self.priv,

                'payload':
                    base64.b64encode(
                        gate.canonical(
                            obj
                        )
                    ).decode()
            }
        )

        signature = (
            subprocess.check_output(
                [
                    'node',
                    '-e',
                    SIGN
                ],
                input=request.encode()
            ).decode()
        )

        obj['signature_b64'] = (
            base64.b64encode(
                bytes(64)
            ).decode()
            if corrupt
            else signature
        )

        body = gate.canonical(
            obj
        )

        self.frame.write_bytes(
            struct.pack(
                '>I',
                len(body)
            ) + body
        )

        self.frame.chmod(
            0o600
        )

    def start(
        self,
        count=2
    ):

        cmd = [

            sys.executable,

            str(
                ROOT /
                'tools/auneya/auneya_transport_v17.py'
            ),

            'serve',

            '--policy',
            str(self.policy),

            '--ledger',
            str(self.ledger),

            '--ready-file',
            str(self.ready),

            '--port',
            '0',

            '--max-connections',
            str(count),

            '--idle-timeout',
            '5'
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.addCleanup(
            self.stop,
            proc
        )

        until = (
            time.monotonic() +
            5
        )

        while not self.ready.exists():

            if proc.poll() is not None:

                out, err = (
                    proc.communicate()
                )

                self.fail(
                    'server exited: ' +
                    err.decode() +
                    out.decode()
                )

            if time.monotonic() > until:

                self.fail(
                    'server did not signal readiness'
                )

            time.sleep(
                .02
            )

        return (
            proc,
            json.loads(
                self.ready.read_text()
            )['port']
        )

    @staticmethod
    def stop(proc):

        if proc.poll() is None:
            proc.terminate()

        try:

            proc.communicate(
                timeout=6
            )

        except subprocess.TimeoutExpired:

            proc.kill()

            proc.communicate()

    def send_raw(
        self,
        port,
        raw,
        halfclose=True
    ):

        with socket.create_connection(
            (
                net.HOST,
                port
            ),
            timeout=3
        ) as s:

            s.settimeout(4)

            s.sendall(raw)

            if halfclose:

                s.shutdown(
                    socket.SHUT_WR
                )

            result = bytearray()

            while not result.endswith(
                b'\n'
            ):

                part = s.recv(
                    512
                )

                if not part:
                    break

                result.extend(part)

                self.assertLess(
                    len(result),
                    513
                )

            return json.loads(
                result
            )

    def test_real_signed_tcp_and_durable_replay_rejection(self):

        proc, port = self.start(2)

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'ACCEPTED'
        )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        proc.wait(
            timeout=5
        )

        with sqlite3.connect(
            self.ledger
        ) as db:

            count = db.execute(
                'SELECT COUNT(*) FROM messages'
            ).fetchone()[0]

            self.assertEqual(
                count,
                1
            )

    def test_forged_signature_does_not_consume_replay(self):

        proc, port = self.start(2)

        self._frame(
            corrupt=True
        )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        self._frame()

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'ACCEPTED'
        )

        proc.wait(
            timeout=5
        )

    def test_oversize_rejected_before_reading_body(self):

        proc, port = self.start(2)

        result = self.send_raw(
            port,
            struct.pack(
                '>I',
                65537
            )
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'ACCEPTED'
        )

        proc.wait(
            timeout=5
        )

    def test_trailing_bytes_rejected_without_consuming(self):

        proc, port = self.start(2)

        result = self.send_raw(
            port,
            self.frame.read_bytes() +
            b'x'
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'ACCEPTED'
        )

        proc.wait(
            timeout=5
        )

    def test_truncated_frame_rejected_without_consuming(self):

        proc, port = self.start(2)

        result = self.send_raw(
            port,
            self.frame.read_bytes()[:-1]
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'ACCEPTED'
        )

        proc.wait(
            timeout=5
        )

    def test_policy_revocation_blocks_next_message(self):

        proc, port = self.start(2)

        net.revoke(
            self.policy
        )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        proc.wait(
            timeout=5
        )

        self.assertFalse(
            self.ledger.exists()
        )

    def test_read_deadline_stops_slow_sender(self):

        proc, port = self.start(2)

        with socket.create_connection(
            (
                net.HOST,
                port
            ),
            timeout=3
        ) as s:

            s.settimeout(4)

            s.sendall(
                b'\x00\x00'
            )

            response = json.loads(
                s.recv(512)
            )

            self.assertEqual(
                response['status'],
                'REJECTED'
            )

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'ACCEPTED'
        )

        proc.wait(
            timeout=5
        )

    def test_loopback_only_and_enrollment_pins(self):

        with self.assertRaisesRegex(
            net.TransportError,
            'loopback'
        ):

            net.send_frame(
                self.frame,
                '0.0.0.0',
                4321
            )

        args = type(
            'Args',
            (),
            {
                'policy':
                    str(
                        self.root /
                        'other.json'
                    ),

                'key':
                    str(self.key),

                'key_sha256':
                    '0' * 64,

                'sender':
                    'phone-alpha',

                'chain_id':
                    'auneya-research-v1',

                'checkpoint_sha256':
                    '3' * 64,

                'challenge_sha256':
                    '1' * 64,

                'manifest_sha256':
                    '2' * 64
            }
        )()

        with self.assertRaises(
            net.TransportError
        ):

            net.enroll(
                args
            )

        self.assertFalse(
            (
                self.root /
                'other.json'
            ).exists()
        )

    def test_rotation_invalidates_old_key(self):

        keys = json.loads(
            subprocess.check_output(
                [
                    'node',
                    '-e',
                    KEYGEN
                ]
            )
        )

        newkey = (
            self.root /
            'other.pem'
        )

        newkey.write_text(
            keys['pub']
        )

        newkey.chmod(
            0o600
        )

        args = type(
            'Args',
            (),
            {
                'policy':
                    str(self.policy),

                'key':
                    str(newkey),

                'key_sha256':
                    gate.sha(
                        newkey.read_bytes()
                    ),

                'sender':
                    'phone-alpha',

                'chain_id':
                    'auneya-research-v1',

                'checkpoint_sha256':
                    '3' * 64,

                'challenge_sha256':
                    '1' * 64,

                'manifest_sha256':
                    '2' * 64
            }
        )()

        net.enroll(
            args,
            rotate=True
        )

        self.assertNotEqual(
            net.load_policy(
                self.policy
            )['key_sha256'],
            self.pin
        )

        proc, port = self.start(1)

        result = net.send_frame(
            self.frame,
            net.HOST,
            port
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        proc.wait(
            timeout=5
        )


if __name__ == '__main__':
    unittest.main()
