#!/usr/bin/env python3
"""WVP 0.5.2 local evidence; not an external attestation."""
import hashlib,hmac,json,subprocess,sys
from pathlib import Path

R=Path(__file__).resolve().parents[1]
FILES=(
 'README.md',
 'Cargo.lock',
 'tools/readme_truth.py',
 'tools/wvp_repro_v052.py',
 'tools/auneya/auneya_gate4_bundle_v118.py'
)
FALSE={
 'audit':False,
 'independent_devices':False,
 'mainnet':False,
 'token':False
}
CMDS=(
 (sys.executable,'tools/readme_truth.py','--check'),
 (sys.executable,'-m','unittest','discover',
  '-s','tests','-p','test_auneya_gate4_bundle_v118.py','-v'),
 ('cargo','test','--workspace','--locked')
)

def canonical(x):
 return (json.dumps(
  x,sort_keys=True,separators=(',',':'),allow_nan=False
 )+'\n').encode()

def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d: raise ValueError('duplicate key')
  d[k]=v
 return d

def decode(raw):
 if not 0<len(raw)<=65536: raise ValueError('length')
 x=json.loads(raw,object_pairs_hook=unique)
 if canonical(x)!=raw or not isinstance(x,dict):
  raise ValueError('canonical')
 if x.get('claims')!=FALSE or x.get('format')!='wvp-local-v1':
  raise ValueError('claims/format')
 return x

def evidence():
 if subprocess.check_output(
  ('git','status','--porcelain'),cwd=R
 ).strip():
  raise ValueError('dirty source')
 commit=subprocess.check_output(
  ('git','rev-parse','HEAD'),cwd=R,text=True
 ).strip()
 hashes={
  p:hashlib.sha256((R/p).read_bytes()).hexdigest()
  for p in FILES
 }
 for cmd in CMDS:
  subprocess.run(cmd,cwd=R,check=True,stdout=subprocess.DEVNULL)
 return {
  'format':'wvp-local-v1',
  'commit':commit,
  'hashes':hashes,
  'checks':[c[1] for c in CMDS],
  'claims':FALSE
 }

if __name__=='__main__':
 if len(sys.argv)!=3 or sys.argv[1] not in ('create','verify'):
  sys.exit('Use: create|verify PATH')
 path=Path(sys.argv[2])
 expected=canonical(evidence())
 if sys.argv[1]=='create':
  with path.open('xb') as f:
   f.write(expected)
 else:
  if path.is_symlink():
   sys.exit('FAIL symlink')
  with path.open('rb') as f:
   raw=f.read(65537)
  if not hmac.compare_digest(
   canonical(decode(raw)),expected
  ):
   sys.exit('FAIL evidence mismatch')
 print('PASS WVP 0.5.2:',hashlib.sha256(expected).hexdigest())
