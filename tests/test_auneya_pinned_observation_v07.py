"""Adversarial, actual Ed25519/SQLite regression suite for pinned observations."""
import hashlib
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools' / 'auneya'))
import auneya_nightfall_challenge_v05 as v5
import auneya_registry_checkpoint_v06 as v6
import auneya_trusted_node_identity_v04 as ids
import auneya_pinned_observation_v07 as v7


def public_status():
    return {'network': 'mainnet', 'genesis': v5.GENESIS, 'protocol_version': 8,
            'tip_height': 25000, 'tip': 'a'*64, 'total_work': '9000000',
            'live_peers': 2, 'best_peer_height': 25000, 'supply_invariant_ok': True,
            'loading': False, 'stalled_on_fork': False, 'reorg_in_flight': False}


@unittest.skipUnless(shutil.which('openssl'), 'OpenSSL required for genuine Ed25519 tests')
class PinnedObservations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='auneya-v07-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.registry = self.root/'registry.sqlite'
        self.seal = self.root/'sealed.json'
        self.replay = self.root/'replay.sqlite'
        self.now = int(time.time())
        self.challenge = v5.new_challenge(self.now)
        self.keys = {}
        for name in ('node_research_operator_a', 'node_research_operator_b'):
            private = self.root/(name+'.key')
            public = self.root/(name+'.pub')
            subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(private)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            private.chmod(0o600)
            subprocess.run(['openssl','pkey','-in',str(private),'-pubout','-out',str(public)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            ids.enroll(self.registry, name, public, ids.fingerprint(ids.key_der(public)))
            self.keys[name] = private
        self.pin = v6.write_new(self.seal, v6.snapshot(self.registry))

    def proof(self, name='node_research_operator_a', status=None):
        return v5.attest(self.challenge, name, self.keys[name],
                         public_status() if status is None else status, self.now)

    def run_verifier(self, receipts, pin=None, replay=None, registry=None):
        return v7.verify_pinned(self.challenge, receipts,
                                self.registry if registry is None else registry,
                                self.seal, self.pin if pin is None else pin,
                                self.replay if replay is None else replay, self.now)

    def test_single_valid_and_replay_refused(self):
        r = self.proof()
        value = self.run_verifier([r])
        self.assertEqual(value['result'], 'PINNED_SIGNED_OBSERVATIONS_VALID')
        self.assertFalse(value['chain_consensus_validated'])
        with self.assertRaises(v5.ChallengeError):
            self.run_verifier([r])

    def test_two_operator_comparison(self):
        a = self.proof()
        b = self.proof('node_research_operator_b')
        value = self.run_verifier([a,b])
        self.assertEqual(value['comparison']['result'], 'MATCHING_TIP_CLAIMS')
        self.assertFalse(value['operator_independence_proven'])

    def test_same_height_conflict_is_reported_not_certified(self):
        bad = public_status()
        bad['tip'] = 'b'*64
        result = self.run_verifier([self.proof(), self.proof('node_research_operator_b',bad)])
        self.assertEqual(result['comparison']['result'], 'SAME_HEIGHT_FORK_CONFLICT')
        self.assertFalse(result['chain_consensus_validated'])

    def test_mutated_signed_receipt_does_not_consume_replay(self):
        original = self.proof()
        edited = {**original, 'status': {**original['status'], 'tip': 'f'*64}}
        with self.assertRaises(v5.ChallengeError):
            self.run_verifier([edited])
        self.run_verifier([original])

    def test_wrong_pin_does_not_consume_replay(self):
        original = self.proof()
        with self.assertRaises(v6.CheckpointError):
            self.run_verifier([original], pin='0'*64)
        self.run_verifier([original])

    def test_unpinned_enrollment_does_not_consume_replay(self):
        with sqlite3.connect(self.registry) as db:
            der = db.execute('SELECT public_der FROM nodes LIMIT 1').fetchone()[0]
            db.execute('INSERT INTO nodes VALUES (?,?,?,?,?)',
                       ('new_operator',0,hashlib.sha256(der).hexdigest(),der,'active'))
            db.execute('INSERT INTO events VALUES (?,?,?,?)',
                       ('new_operator',0,'b'*64,'enroll'))
        with self.assertRaises((v6.CheckpointError, v7.PinnedError)):
            self.run_verifier([self.proof()])
        self.assertFalse(self.replay.exists())

    def test_registry_rollback_against_new_checkpoint(self):
        original_db = self.root/'original.sqlite'
        with sqlite3.connect(self.registry) as src, sqlite3.connect(original_db) as dst:
            src.backup(dst)
        original_db.chmod(0o600)
        name = 'node_research_operator_a'
        rev = ids.revocation_request(self.registry, name, self.keys[name])
        ids.apply_event(self.registry, rev, name)
        newer = self.root/'newer.json'
        new_pin = v6.write_new(newer, v6.advance(self.registry, self.seal, self.pin))
        with sqlite3.connect(original_db) as src, sqlite3.connect(self.registry) as dst:
            src.backup(dst)
        with self.assertRaises(v7.PinnedError):
            v7.verify_pinned(self.challenge,[self.proof()],self.registry,newer,new_pin,self.replay,self.now)
        self.assertFalse(self.replay.exists())

    def test_refuses_replay_path_aliasing_inputs(self):
        for target in (self.registry, self.seal):
            with self.subTest(target=target), self.assertRaises(v7.PinnedError):
                self.run_verifier([self.proof()], replay=target)

    def test_fails_expired_challenge(self):
        with self.assertRaises(v5.ChallengeError):
            v7.verify_pinned(self.challenge,[self.proof()],self.registry,self.seal,
                             self.pin,self.replay,self.now+900)

    def test_no_same_operator_quorum(self):
        a = self.proof()
        with self.assertRaises(v5.ChallengeError):
            self.run_verifier([a,a])
        self.assertFalse(self.replay.exists())

    def test_symlink_registry_rejected(self):
        link = self.root/'link.sqlite'
        link.symlink_to(self.registry)
        with self.assertRaises(v6.CheckpointError):
            self.run_verifier([self.proof()], registry=link)
        self.assertFalse(self.replay.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
