"""Lossless v1.4: signed uint64, parser attacks and full v1.3 adversarial parity."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'/'auneya'),str(ROOT/'tests')]
import auneya_archive_v09 as v9
import auneya_federation_v11 as f11
import auneya_nightfall_challenge_v05 as v5
import auneya_portable_v12 as p12
import auneya_registry_checkpoint_v06 as v6
from test_auneya_wvp_evidence_batch_v08 import EvidenceBatch, status
from test_auneya_independent_v13 import IndependentVerifierV13
NODE=shutil.which('node')
PARSER=ROOT/'tools/auneya/auneya_lossless_json_v14.js'
VERIFY=ROOT/'tools/auneya/auneya_independent_v14.js'

@unittest.skipUnless(NODE and shutil.which('openssl'),'Node and OpenSSL required')
class V14Lossless(unittest.TestCase):
    def parse(self,raw):
        snippet=(
            "const fs=require('node:fs'),p=require(process.argv[1]);"
            "try{const v=p.parseLossless(fs.readFileSync(0));"
            "process.stdout.write(typeof v==='bigint'?v.toString():JSON.stringify(v));}"
            "catch(e){console.error(e.message);process.exitCode=2;}"
        )
        return subprocess.run([NODE,'-e',snippet,str(PARSER)],input=raw,capture_output=True,timeout=15)

    def test_exact_integer_boundaries(self):
        for number in [0,1,-1,2**53-1,2**53,2**53+1,2**63+17,2**64-1,-(2**64)]:
            with self.subTest(number=number):
                r=self.parse(str(number).encode())
                self.assertEqual(r.returncode,0,r.stderr.decode())
                self.assertEqual(r.stdout.decode(),str(number))

    def test_adversarial_parser(self):
        bad=[b'{"x":1,"x":2}',b'{"__proto__":1,"__proto__":2}',b'{"x":1.0}',b'{"x":1e2}',b'{"x":01}',b'{"x":NaN}',b'{"x":1,}',b'[1,]',b'1 2',b'"bad\x01"',b'"\\uZZZZ"',b'\xff',b'['*70+b'0'+b']'*70]
        for data in bad:
            with self.subTest(data=data[:50]):
                r=self.parse(data)
                self.assertEqual(r.returncode,2,r.stdout.decode())
        r=self.parse(b'{"__proto__":1,"constructor":2}')
        self.assertEqual(r.returncode,0,r.stderr.decode())
        self.assertEqual(json.loads(r.stdout),{'__proto__':1,'constructor':2})

    def test_signed_uint64_cross_language_parity(self):
        fx=EvidenceBatch('test_three_valid_operators')
        fx.setUp()
        self.addCleanup(fx.doCleanups)
        names=list(fx.privates)
        heights={names[0]:2**53+1,names[1]:2**63+7,names[2]:2**64-1}
        chash=f11.sha(v5.canonical(fx.challenge))
        store=fx.root/'federation-v14.sqlite'
        bundle=fx.root/'bundle-v14'
        for index,group in enumerate((names[:2],names[1:])):
            receipts=[fx.receipt(name,status(height=heights[name])) for name in group]
            capsule=v9.capture(fx.challenge,receipts,fx.registry,fx.seal,fx.pin,fx.root/f'replay-{index}.sqlite',fx.now)
            cap=fx.root/f'capsule-{index}.json'
            v6.write_new(cap,capsule)
            f11.ingest(store,cap,fx.pin,chash)
        exported=p12.export(store,fx.pin,chash,bundle)
        expected=exported['manifest_sha256']
        py=p12.verify(bundle,fx.pin,chash,expected)
        result=subprocess.run([NODE,str(VERIFY),'verify','--bundle',str(bundle),'--pin',fx.pin,'--challenge-sha256',chash,'--expected-manifest-sha256',expected],text=True,capture_output=True,timeout=45)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.assertEqual(json.loads(result.stdout),py)
        self.assertEqual(py['capsule_count'],2)

@unittest.skipUnless(NODE and shutil.which('openssl'),'Node and OpenSSL required')
class V14AdversarialRegression(IndependentVerifierV13):
    def node(self,manifest_hash,pin=None,challenge=None):
        return subprocess.run([NODE,str(VERIFY),'verify','--bundle',str(self.bundle),'--pin',pin if pin is not None else self.pin,'--challenge-sha256',challenge if challenge is not None else self.challenge_hash,'--expected-manifest-sha256',manifest_hash],text=True,capture_output=True,timeout=35)

# Do not collect the imported v1.3 class a second time here.
del IndependentVerifierV13

if __name__=='__main__':
    unittest.main()
