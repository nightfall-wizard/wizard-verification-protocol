import hashlib,json,subprocess,sys,unittest
from pathlib import Path

R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tests'),str(R/'tools/auneya')]

import auneya_capsule_v112 as cap
import test_auneya_quorum_v111 as base

class DualTests(unittest.TestCase):
 def setUp(self):
  f=base.MultiKeeperTests('test_authenticated_quorum_and_determinism')
  f.setUp()
  self.addCleanup(f.doCleanups)
  self.f=f
  self.c=f.root/'v117.json'
  cap.export_capsule(f.trust,f.b1,self.c)

 def call(self,h=None,extra=()):
  h=h or hashlib.sha256(self.c.read_bytes()).hexdigest()
  return subprocess.run([
   sys.executable,str(R/'tools/auneya/auneya_dual_v117.py'),
   '--trust',str(self.f.trust),
   '--capsule',str(self.c),
   '--expected',h,*extra
  ],capture_output=True,text=True,timeout=90)

 def test_verified_deterministic(self):
  a=self.call()
  b=self.call()
  self.assertEqual(a.returncode,0,a.stderr)
  self.assertEqual(a.stdout,b.stdout)
  o=json.loads(a.stdout)
  self.assertTrue(o['python_verified'] and o['node_verified'])
  self.assertFalse(o['independent_devices_proven'])

 def test_external_hash_reject(self):
  self.assertNotEqual(self.call('0'*64).returncode,0)

 def test_report_exclusive(self):
  p=self.f.root/'report.json'
  a=self.call(extra=('--report',str(p)))
  self.assertEqual(a.returncode,0,a.stderr)
  self.assertEqual(p.read_text(),a.stdout)
  self.assertNotEqual(self.call(extra=('--report',str(p))).returncode,0)

 def test_forgery_rejected(self):
  b=json.loads(self.c.read_text())
  b['quorum_report_sha256']='0'*64
  self.c.write_text(json.dumps(b,sort_keys=True,separators=(',',':'))+'\n')
  self.c.chmod(0o600)
  self.assertNotEqual(self.call().returncode,0)
