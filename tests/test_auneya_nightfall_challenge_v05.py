#!/usr/bin/env python3
"""Adversarial regressions for challenge-bound read-only Nightfall witnesses."""
import copy
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/auneya'))
import auneya_nightfall_challenge_v05 as p
import auneya_trusted_node_identity_v04 as ident


def node():
    return {'network':'mainnet','genesis':p.GENESIS,'protocol_version':8,
            'tip_height':1800,'tip':'a'*64,'total_work':'990000',
            'live_peers':2,'best_peer_height':1800,'supply_invariant_ok':True,
            'loading':False,'stalled_on_fork':False,'reorg_in_flight':False}


class ProofTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='auneya-v05-tests-')
        self.addCleanup(self.tmp.cleanup)
        self.d=Path(self.tmp.name)
        self.db=self.d/'registry.sqlite'
        self.ledger=self.d/'used.sqlite'
        self.now=int(time.time())
        self.c=p.new_challenge(self.now)
        self.keys={}
        for name in ('node_research_operator_a','node_research_operator_b'):
            private=self.d/(name+'.private.pem')
            public=self.d/(name+'.pub.pem')
            subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(private)],
                           check=True,capture_output=True)
            private.chmod(0o600)
            subprocess.run(['openssl','pkey','-in',str(private),'-pubout','-out',str(public)],
                           check=True,capture_output=True)
            fp=ident.fingerprint(ident.key_der(public))
            ident.enroll(self.db,name,public,fp)
            self.keys[name]=private

    def receipt(self,name='node_research_operator_a',status=None):
        return p.attest(self.c,name,self.keys[name],node() if status is None else status,self.now)

    def verified(self,receipt):
        return p.verify_receipt(self.c,receipt,self.db,self.now)

    def test_signatures_are_trusted_and_challenge_bound(self):
        r=self.receipt()
        self.assertEqual(self.verified(r),r)
        for attack in ('tip','total_work','supply_invariant_ok','genesis','protocol_version'):
            t=copy.deepcopy(r)
            if attack=='tip':t['status'][attack]='f'*64
            elif attack=='total_work':t['status'][attack]='990001'
            elif attack=='supply_invariant_ok':t['status'][attack]=False
            elif attack=='genesis':t['status'][attack]='f'*64
            else:t['status'][attack]=9
            with self.subTest(attack=attack),self.assertRaises(p.ChallengeError):self.verified(t)

    def test_unsigned_forged_and_unknown_fields_rejected(self):
        r=self.receipt()
        for t in ({k:v for k,v in r.items() if k!='signature_hex'},
                  {**r,'signature_hex':'00'*64}, {**r,'extra':'value'}):
            with self.assertRaises(p.ChallengeError):self.verified(t)

    def test_wrong_or_expired_challenge(self):
        with self.assertRaises(p.ChallengeError):
            p.verify_receipt({**self.c,'nonce':'f'*64},self.receipt(),self.db,self.now)
        with self.assertRaises(p.ChallengeError):
            p.verify_receipt(self.c,self.receipt(),self.db,self.now+1000)
        with self.assertRaises(p.ChallengeError):
            p.attest({**self.c,'genesis':'0'*64},'node_research_operator_a',
                     self.keys['node_research_operator_a'],node(),self.now)

    def test_bad_rpc_fields_and_types(self):
        for patch_name,bad in (('tip_height',True),('total_work','0003'),
                               ('live_peers',-1),('loading',1),('tip','z'*64),
                               ('best_peer_height',2**65)):
            s=node();s[patch_name]=bad
            with self.subTest(patch_name=patch_name),self.assertRaises(p.ChallengeError):
                p.check_status(s,self.c)

    def test_no_implicit_foreign_json_or_duplicate_keys(self):
        with self.assertRaises(p.ChallengeError):p.strict_json(b'{"nonce":1,"nonce":2}')
        with self.assertRaises(p.ChallengeError):p.strict_json(b'{"x":NaN}')
        with self.assertRaises(p.ChallengeError):p.strict_json(b'{"x":1.0}')
        with self.assertRaises(p.ChallengeError):p.strict_json(b'{' + b'a'*8193 + b'}')

    def test_atomic_replay_block_and_two_operator_comparison(self):
        a=self.verified(self.receipt())
        b=self.verified(self.receipt('node_research_operator_b'))
        p.record_once(self.ledger,[a,b])
        with self.assertRaises(p.ChallengeError):p.record_once(self.ledger,[a])
        self.assertEqual(p.compare_verified(a,b)['result'],'MATCHING_TIP_CLAIMS')
        self.assertFalse(p.compare_verified(a,b)['operator_independence_proven'])

    def test_atomic_replay_rollback(self):
        a=self.verified(self.receipt())
        with self.assertRaises(p.ChallengeError):p.record_once(self.ledger,[a,a])
        p.record_once(self.ledger,[a])

    def test_fork_conflict_without_false_cross_height_proof(self):
        a=self.verified(self.receipt())
        s=node();s['tip']='b'*64
        b=self.verified(self.receipt('node_research_operator_b',s))
        self.assertEqual(p.compare_verified(a,b)['result'],'SAME_HEIGHT_FORK_CONFLICT')
        s['tip_height']+=1
        c=self.verified(self.receipt('node_research_operator_b',s))
        self.assertEqual(p.compare_verified(a,c)['result'],'INCOMPARABLE_HEIGHTS_NOT_A_FORK_PROOF')
        with self.assertRaises(p.ChallengeError):p.compare_verified(a,a)

    def test_supply_failed_reports_are_not_certificates(self):
        s=node();s['supply_invariant_ok']=False;s['live_peers']=0
        b=self.verified(self.receipt('node_research_operator_b',s))
        a=self.verified(self.receipt())
        self.assertTrue(p.compare_verified(a,b)['reported_risk_flags'])

    def test_key_permissions_required(self):
        key=self.keys['node_research_operator_a'];key.chmod(0o644)
        with self.assertRaises(p.ChallengeError):self.receipt()

    def test_registry_revocation_fails_closed(self):
        r=self.receipt()
        name='node_research_operator_a'
        rev=ident.revocation_request(self.db,name,self.keys[name])
        ident.apply_event(self.db,rev,name)
        with self.assertRaises(p.ChallengeError):self.verified(r)

    def test_file_exclusive_and_private(self):
        out=self.d/'challenge.json'
        p.exclusive_write(out,self.c)
        self.assertEqual(p.read(out),self.c)
        self.assertEqual(out.stat().st_mode & 0o777,0o600)
        with self.assertRaises(p.ChallengeError):p.exclusive_write(out,self.c)
        link=self.d/'link.json';link.symlink_to(out)
        with self.assertRaises(p.ChallengeError):p.read(link)

    def test_local_rpc_framing_and_read_only_request(self):
        ready=threading.Event();port=[];req=[]
        def server():
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',0));sock.listen();port.append(sock.getsockname()[1]);ready.set()
                conn,_=sock.accept()
                with conn:
                    req.append(conn.recv(2048))
                    conn.sendall(p.canonical({'id':1,'result':node()})+b'\n')
        t=threading.Thread(target=server,daemon=True);t.start()
        self.assertTrue(ready.wait(2))
        self.assertEqual(p.local_status(port[0])['tip_height'],1800)
        self.assertEqual(json.loads(req[0])['method'],'status')
        t.join(2)


if __name__=='__main__':
    unittest.main(verbosity=2)
