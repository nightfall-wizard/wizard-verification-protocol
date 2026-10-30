"""
AUNEYA v1.8 regression tests.

Real Ed25519.
TCP loopback.
Forged responses.
Replay protection.
Persistent SQLite.
Revocation.
"""

import base64
import json
from pathlib import Path
import socket
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

import auneya_peer_gate_v16 as gate
import auneya_transport_v17 as v17
import auneya_receipt_v18 as v18


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
let chunks=[];
process.stdin.on('data',x=>chunks.push(x));
process.stdin.on('end',()=>{
    const obj=JSON.parse(
        Buffer.concat(chunks)
    );
    const payload=Buffer.concat([
        Buffer.from('AUNEYA/WVP:PEER:V1.6\\0'),
        Buffer.from(obj.body,'base64')
    ]);
    const sig=c.sign(
        null,
        payload,
        c.createPrivateKey(obj.private)
    );
    process.stdout.write(
        sig.toString('base64')
    );
});
"""


class SignedReceiptTests(unittest.TestCase):

    def setUp(self):

        temp = tempfile.TemporaryDirectory(
            prefix='auneya-v18-'
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

        self.policy = (
            self.root /
            'policy.json'
        )

        self.ledger = (
            self.root /
            'replay.sqlite'
        )

        self.ready = (
            self.root /
            'ready.json'
        )

        self.frame = (
            self.root /
            'frame.bin'
        )

        self.peer = json.loads(
            subprocess.check_output(
                ['node', '-e', KEYGEN]
            )
        )

        self.server = json.loads(
            subprocess.check_output(
                ['node', '-e', KEYGEN]
            )
        )

        self.peer_public = (
            self.root /
            'peer.pem'
        )

        self.server_public = (
            self.root /
            'server.pub.pem'
        )

        self.server_private = (
            self.root /
            'server.key.pem'
        )

        for path, content in (
            (
                self.peer_public,
                self.peer['pub']
            ),
            (
                self.server_public,
                self.server['pub']
            ),
            (
                self.server_private,
                self.server['priv']
            )
        ):

            path.write_text(
                content
            )

            path.chmod(
                0o600
            )

        self.peer_pin = gate.sha(
            self.peer_public.read_bytes()
        )

        self.server_pin = gate.sha(
            self.server_public.read_bytes()
        )

        args = type(
            'Args',
            (),
            {
                'policy':
                    str(self.policy),

                'key':
                    str(self.peer_public),

                'key_sha256':
                    self.peer_pin,

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

        v17.enroll(
            args
        )

        self.make_frame()


    def make_frame(self, invalid=False):

        now = int(
            time.time()
        )

        payload = {
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
                now - 1,

            'expires_at':
                now + 70,

            'challenge_sha256':
                '1' * 64,

            'manifest_sha256':
                '2' * 64,

            'checkpoint_sha256':
                '3' * 64,

            'public_key_sha256':
                self.peer_pin
        }

        request = json.dumps({
            'private':
                self.peer['priv'],

            'body':
                base64.b64encode(
                    gate.canonical(
                        payload
                    )
                ).decode()
        })

        signature = subprocess.check_output(
            ['node', '-e', SIGN],
            input=request.encode()
        ).decode()

        payload['signature_b64'] = (
            base64.b64encode(
                bytes(64)
            ).decode()
            if invalid
            else signature
        )

        body = gate.canonical(
            payload
        )

        frame = (
            struct.pack(
                '>I',
                len(body)
            ) +
            body
        )

        self.frame.write_bytes(
            frame
        )

        self.frame.chmod(
            0o600
        )


    def start(self, attempts=1):

        command = [
            sys.executable,

            str(
                ROOT /
                'tools/auneya/auneya_receipt_v18.py'
            ),

            'serve',

            '--policy',
            str(self.policy),

            '--ledger',
            str(self.ledger),

            '--ready-file',
            str(self.ready),

            '--server-private',
            str(self.server_private),

            '--server-public',
            str(self.server_public),

            '--server-pin',
            self.server_pin,

            '--port',
            '0',

            '--max-connections',
            str(attempts),

            '--idle-timeout',
            '5'
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.addCleanup(
            self.stop,
            process
        )

        deadline = (
            time.monotonic() + 6
        )

        while not self.ready.exists():

            if process.poll() is not None:

                stdout, stderr = (
                    process.communicate()
                )

                self.fail(
                    'server failed: ' +
                    (
                        stdout + stderr
                    ).decode()
                )

            self.assertLess(
                time.monotonic(),
                deadline,
                'server startup timeout'
            )

            time.sleep(
                0.02
            )

        port = json.loads(
            self.ready.read_text()
        )['port']

        return process, port


    @staticmethod
    def stop(process):

        if process.poll() is None:
            process.terminate()

        try:

            process.communicate(
                timeout=6
            )

        except subprocess.TimeoutExpired:

            process.kill()
            process.communicate()


    def test_authenticated_acceptance(self):

        process, port = self.start()

        result = v18.send(
            self.frame,
            v17.HOST,
            port,
            self.server_public,
            self.server_pin
        )

        self.assertEqual(
            result['status'],
            'ACCEPTED'
        )

        self.assertTrue(
            result['authenticated_ack']
        )

        self.assertTrue(
            result['local_replay_persisted']
        )

        process.wait(
            timeout=6
        )


    def test_durable_replay_after_restart(self):

        process, port = self.start()

        first = v18.send(
            self.frame,
            v17.HOST,
            port,
            self.server_public,
            self.server_pin
        )

        self.assertEqual(
            first['status'],
            'ACCEPTED'
        )

        process.wait(
            timeout=6
        )

        restarted, port = self.start()

        second = v18.send(
            self.frame,
            v17.HOST,
            port,
            self.server_public,
            self.server_pin
        )

        self.assertEqual(
            second['status'],
            'REJECTED'
        )

        self.assertTrue(
            second['authenticated_ack']
        )

        restarted.wait(
            timeout=6
        )


    def test_forged_peer_does_not_consume_replay(self):

        process, port = self.start(2)

        self.make_frame(
            invalid=True
        )

        rejected = v18.send(
            self.frame,
            v17.HOST,
            port,
            self.server_public,
            self.server_pin
        )

        self.assertEqual(
            rejected['status'],
            'REJECTED'
        )

        self.make_frame()

        accepted = v18.send(
            self.frame,
            v17.HOST,
            port,
            self.server_public,
            self.server_pin
        )

        self.assertEqual(
            accepted['status'],
            'ACCEPTED'
        )

        process.wait(
            timeout=6
        )


    def test_wrong_server_pin(self):

        with self.assertRaisesRegex(
            ValueError,
            'pin mismatch'
        ):

            v18.send(
                self.frame,
                v17.HOST,
                17018,
                self.server_public,
                '0' * 64
            )


    def test_signed_receipt_nonce_replay_rejected(self):

        frame = self.frame.read_bytes()

        nonce = bytes(
            [88]
        ) * 32

        receipt = {
            'format':
                v18.FORMAT,

            'chain_id':
                'auneya-research-v1',

            'sender':
                'phone-alpha',

            'status':
                'ACCEPTED',

            'frame_sha256':
                gate.sha(frame),

            'nonce_b64':
                base64.b64encode(
                    nonce
                ).decode(),

            'responder_key_sha256':
                self.server_pin,

            'local_replay_persisted':
                True,

            'non_value_research_only':
                True
        }

        wire = v18.signed_receipt(
            receipt,
            self.server_private.read_bytes()
        )

        verified = v18.verify_receipt(
            wire,
            self.server_public.read_bytes(),
            self.server_pin,
            nonce,
            frame
        )

        self.assertEqual(
            verified['status'],
            'ACCEPTED'
        )

        with self.assertRaisesRegex(
            ValueError,
            'binding'
        ):

            v18.verify_receipt(
                wire,
                self.server_public.read_bytes(),
                self.server_pin,
                bytes([89]) * 32,
                frame
            )


    def test_modified_receipt_signature_rejected(self):

        frame = self.frame.read_bytes()

        nonce = bytes(
            [88]
        ) * 32

        receipt = {
            'format':
                v18.FORMAT,

            'chain_id':
                'auneya-research-v1',

            'sender':
                'phone-alpha',

            'status':
                'ACCEPTED',

            'frame_sha256':
                gate.sha(frame),

            'nonce_b64':
                base64.b64encode(
                    nonce
                ).decode(),

            'responder_key_sha256':
                self.server_pin,

            'local_replay_persisted':
                True,

            'non_value_research_only':
                True
        }

        wire = v18.signed_receipt(
            receipt,
            self.server_private.read_bytes()
        )

        modified = json.loads(
            wire
        )

        modified['receipt']['status'] = (
            'REJECTED'
        )

        modified['receipt'][
            'local_replay_persisted'
        ] = False

        tampered = (
            gate.canonical(modified) +
            b'\n'
        )

        with self.assertRaisesRegex(
            ValueError,
            'signature'
        ):

            v18.verify_receipt(
                tampered,
                self.server_public.read_bytes(),
                self.server_pin,
                nonce,
                frame
            )


    def test_attacker_key_cannot_forge_server(self):

        frame = self.frame.read_bytes()

        nonce = bytes(
            [88]
        ) * 32

        receipt = {
            'format':
                v18.FORMAT,

            'chain_id':
                'auneya-research-v1',

            'sender':
                'phone-alpha',

            'status':
                'ACCEPTED',

            'frame_sha256':
                gate.sha(frame),

            'nonce_b64':
                base64.b64encode(
                    nonce
                ).decode(),

            'responder_key_sha256':
                self.server_pin,

            'local_replay_persisted':
                True,

            'non_value_research_only':
                True
        }

        attacker = json.loads(
            subprocess.check_output(
                ['node', '-e', KEYGEN]
            )
        )

        forged = v18.signed_receipt(
            receipt,
            attacker['priv'].encode()
        )

        with self.assertRaisesRegex(
            ValueError,
            'signature'
        ):

            v18.verify_receipt(
                forged,
                self.server_public.read_bytes(),
                self.server_pin,
                nonce,
                frame
            )


    def test_invalid_frame_has_no_trusted_ack(self):

        process, port = self.start()

        with socket.create_connection(
            (
                v17.HOST,
                port
            ),
            timeout=3
        ) as connection:

            connection.settimeout(5)

            connection.sendall(
                bytes([90]) * 32 +
                b'\x00\x00\x00\x01X'
            )

            connection.shutdown(
                socket.SHUT_WR
            )

            response = connection.recv(
                256
            )

        self.assertNotIn(
            b'signature_b64',
            response
        )

        process.wait(
            timeout=6
        )


    def test_revocation_blocks_admission(self):

        process, port = self.start()

        v17.revoke(
            self.policy
        )

        result = v18.send(
            self.frame,
            v17.HOST,
            port,
            self.server_public,
            self.server_pin
        )

        self.assertEqual(
            result['status'],
            'REJECTED'
        )

        process.wait(
            timeout=6
        )


if __name__ == '__main__':
    unittest.main()
