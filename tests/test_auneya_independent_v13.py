"""
Cross-language AUNEYA/WVP v1.3 conformance.

Real Ed25519-signed capsules are produced
by the existing v0.8/v0.9 stack.
"""

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

sys.path[:0] = [
    str(ROOT / 'tools' / 'auneya'),
    str(ROOT / 'tests')
]

import auneya_archive_v09 as v9
import auneya_federation_v11 as f11
import auneya_nightfall_challenge_v05 as v5
import auneya_portable_v12 as p12
import auneya_registry_checkpoint_v06 as v6

from test_auneya_wvp_evidence_batch_v08 import EvidenceBatch

NODE = shutil.which('node')


@unittest.skipUnless(
    NODE and shutil.which('openssl'),
    'Node.js and OpenSSL are mandatory'
)
class IndependentVerifierV13(unittest.TestCase):

    def setUp(self):
        self.f = EvidenceBatch(
            'test_three_valid_operators'
        )

        self.f.setUp()

        self.addCleanup(
            self.f.doCleanups
        )

        self.ops = list(self.f.privates)

        self.store = (
            self.f.root / 'federation-v13.sqlite'
        )

        self.challenge_hash = f11.sha(
            v5.canonical(self.f.challenge)
        )

        self.pin = self.f.pin

        self.bundle = (
            self.f.root / 'portable-v13'
        )

    def prepare(self):
        a,b,c = self.ops

        for i,names in enumerate(
            ([a,b], [b,c])
        ):
            obj = v9.capture(
                self.f.challenge,
                [self.f.receipt(n) for n in names],
                self.f.registry,
                self.f.seal,
                self.pin,
                self.f.root /
                    ('v13-replay-%d.sqlite' % i),
                self.f.now
            )

            cap = (
                self.f.root /
                ('v13-source-%d.json' % i)
            )

            v6.write_new(cap,obj)

            f11.ingest(
                self.store,
                cap,
                self.pin,
                self.challenge_hash
            )

        return p12.export(
            self.store,
            self.pin,
            self.challenge_hash,
            self.bundle
        )

    def node(
        self,
        manifest_hash,
        pin=None,
        challenge=None
    ):
        return subprocess.run(
            [
                NODE,
                str(
                    ROOT /
                    'tools/auneya/auneya_independent_v13.js'
                ),
                'verify',
                '--bundle',
                str(self.bundle),
                '--pin',
                pin if pin is not None else self.pin,
                '--challenge-sha256',
                (
                    challenge
                    if challenge is not None
                    else self.challenge_hash
                ),
                '--expected-manifest-sha256',
                manifest_hash
            ],
            text=True,
            capture_output=True,
            timeout=30
        )

    def python_accepts(self, manifest_hash):
        try:
            p12.verify(
                self.bundle,
                self.pin,
                self.challenge_hash,
                manifest_hash
            )
            return True

        except (
            ValueError,
            OSError,
            KeyError,
            TypeError
        ):
            return False

    def rewrite_manifest(self, changed):
        f = self.bundle / 'manifest.json'

        obj = json.loads(
            f.read_bytes()
        )

        changed(obj)

        raw = v6.canonical(obj)
        f.write_bytes(raw)

        return hashlib.sha256(
            raw
        ).hexdigest()

    def assert_rejected_both(self, digest):
        self.assertFalse(
            self.python_accepts(digest),
            'Python accepted malicious bundle'
        )

        result = self.node(digest)

        self.assertEqual(
            result.returncode,
            2,
            result.stdout + result.stderr
        )

        self.assertIn(
            'FAIL-CLOSED:',
            result.stderr
        )

    def test_positive_exact_result_parity(self):
        exported = self.prepare()

        digest = exported['manifest_sha256']

        py = p12.verify(
            self.bundle,
            self.pin,
            self.challenge_hash,
            digest
        )

        js = self.node(digest)

        self.assertEqual(
            js.returncode,
            0,
            js.stderr
        )

        self.assertEqual(
            json.loads(js.stdout),
            py
        )

        self.assertEqual(
            py['capsule_count'],
            2
        )

    def test_mismatched_external_manifest_pin(self):
        digest = self.prepare()[
            'manifest_sha256'
        ]

        self.assert_rejected_both(
            '0' * 64
        )

        self.assertEqual(
            self.node(
                digest,
                pin='0' * 64
            ).returncode,
            2
        )

        self.assertEqual(
            self.node(
                digest,
                challenge='0' * 64
            ).returncode,
            2
        )

    def test_missing_capsule(self):
        digest = self.prepare()[
            'manifest_sha256'
        ]

        next(
            (self.bundle/'capsules').iterdir()
        ).unlink()

        self.assert_rejected_both(digest)

    def test_extra_file(self):
        digest = self.prepare()[
            'manifest_sha256'
        ]

        (
            self.bundle/'extra'
        ).write_text('not declared')

        self.assert_rejected_both(digest)

    def test_capsule_symlink(self):
        digest = self.prepare()[
            'manifest_sha256'
        ]

        cap = next(
            (self.bundle/'capsules').iterdir()
        )

        held = (
            self.f.root/'held-v13.json'
        )

        cap.rename(held)
        cap.symlink_to(held)

        self.assert_rejected_both(digest)

    def test_repinned_forged_report(self):
        self.prepare()

        digest = self.rewrite_manifest(
            lambda m:
                m['federation_report'].update(
                    signer_identity_count=777
                )
        )

        self.assert_rejected_both(digest)

    def test_repinned_duplicate_capsule_reference(self):
        self.prepare()

        digest = self.rewrite_manifest(
            lambda m:
                m['capsules'].append(
                    copy.deepcopy(
                        m['capsules'][0]
                    )
                )
        )

        self.assert_rejected_both(digest)

    def test_repinned_invalid_signature(self):
        self.prepare()

        capdir = self.bundle/'capsules'

        cap = next(
            capdir.iterdir()
        )

        obj = json.loads(
            cap.read_bytes()
        )

        signature = (
            obj['receipts'][0]['signature_hex']
        )

        obj['receipts'][0]['signature_hex'] = (
            (
                '0'
                if signature[0] != '0'
                else '1'
            )
            + signature[1:]
        )

        raw = v6.canonical(obj)

        old = cap.name[:-5]

        new = hashlib.sha256(
            raw
        ).hexdigest()

        cap.unlink()

        replacement = (
            capdir/(new+'.json')
        )

        replacement.write_bytes(raw)
        replacement.chmod(0o600)

        def edit(m):
            for e in m['capsules']:
                if e['sha256'] == old:
                    e.update(
                        sha256=new,
                        file='capsules/'+new+'.json',
                        size_bytes=len(raw)
                    )

            m['capsules'].sort(
                key=lambda e:e['sha256']
            )

        digest = self.rewrite_manifest(edit)

        self.assert_rejected_both(digest)


if __name__ == '__main__':
    unittest.main()
