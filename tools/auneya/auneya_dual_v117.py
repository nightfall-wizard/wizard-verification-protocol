#!/usr/bin/env python3
"""AUNEYA v1.17: offline, independent Python+Node quorum verification."""
import argparse,hashlib,json,os,stat,subprocess,sys,tempfile
from pathlib import Path

P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import auneya_capsule_v112 as cap

sha=lambda b:hashlib.sha256(b).hexdigest()

def read(p,n,private=False):
 p=Path(p).absolute()
 m=p.parent.lstat().st_mode
 if not stat.S_ISDIR(m) or stat.S_ISLNK(m) or (private and m&0o077):
  raise ValueError('unsafe directory')
 fd=os.open(p,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
 try:
  st=os.fstat(fd)
  if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1 or not 0<st.st_size<=n or (private and st.st_mode&0o077):
   raise ValueError('unsafe file')
  with os.fdopen(os.dup(fd),'rb') as f:
   b=f.read(n+1)
  if len(b)!=st.st_size:
   raise ValueError('changed file')
  return b
 finally:
  os.close(fd)

def run(a):
 if len(a.expected)!=64 or any(c not in '0123456789abcdef' for c in a.expected):
  raise ValueError('external SHA256 required')

 t=read(a.trust,32768,True)
 b=read(a.capsule,3*1024*1024)

 if sha(b)!=a.expected:
  raise ValueError('external capsule hash mismatch')

 p=cap.verify_capsule(a.trust,a.capsule)

 if p.get('signatures_verified') is not True or p.get('floor_status')!='not_configured':
  raise ValueError('Python quorum rejected')

 cmd=[
  'node',
  str(P/'auneya_gate3_full_v116.js'),
  '--trust',a.trust,
  '--capsule',a.capsule,
  '--expected-capsule',a.expected
 ]

 x=subprocess.run(cmd,capture_output=True,text=True,timeout=60)

 if x.returncode or len(x.stdout)>32768:
  raise ValueError('independent Node quorum rejected')

 n=json.loads(x.stdout)

 if n.get('quorum_signatures_verified') is not True or n.get('expected_capsule_matched') is not True:
  raise ValueError('Node quorum rejected')

 for k in ('chain_id','capsule_sha256','anchor_sha256','keeper_count','required_quorum'):
  if p.get(k)!=n.get(k):
   raise ValueError('runtime disagreement: '+k)

 if str(p['sequence'])!=n.get('sequence_decimal'):
  raise ValueError('sequence disagreement')

 for k in (
  'independent_devices_proven',
  'external_retention_proven',
  'independent_audit_completed',
  'economic_activation',
  'mainnet_active'
 ):
  if n.get(k) is not False:
   raise ValueError('unsafe Node claim: '+k)

 if p.get('non_value_research_only') is not True or n.get('non_value_research_only') is not True:
  raise ValueError('unsafe activation claim')

 if sha(read(a.trust,32768,True))!=sha(t) or sha(read(a.capsule,3*1024*1024))!=a.expected:
  raise ValueError('inputs changed')

 return dict(
  format='auneya-dual-runtime-v1.17',
  chain_id=n['chain_id'],
  sequence=n['sequence_decimal'],
  capsule_sha256=a.expected,
  trust_sha256=sha(t),
  anchor_sha256=n['anchor_sha256'],
  quorum_report_sha256=n['quorum_report_sha256'],
  keeper_count=n['keeper_count'],
  required_quorum=n['required_quorum'],
  python_verified=True,
  node_verified=True,
  independent_devices_proven=False,
  external_retention_proven=False,
  independent_audit_completed=False,
  economic_activation=False,
  mainnet_active=False,
  non_value_research_only=True
 )

def main():
 ap=argparse.ArgumentParser()
 for k in ('trust','capsule','expected'):
  ap.add_argument('--'+k,required=True)
 ap.add_argument('--report')
 a=ap.parse_args()

 b=(json.dumps(run(a),sort_keys=True,separators=(',',':'))+'\n').encode()

 if a.report:
  p=Path(a.report).absolute()
  m=p.parent.lstat().st_mode

  if not stat.S_ISDIR(m) or m&0o077 or p.exists() or p.is_symlink():
   raise ValueError('unsafe report destination')

  fd=os.open(
   p,
   os.O_WRONLY|os.O_CREAT|os.O_EXCL|
   getattr(os,'O_NOFOLLOW',0),
   0o600
  )

  try:
   with os.fdopen(fd,'wb') as f:
    f.write(b)
    f.flush()
    os.fsync(f.fileno())
  except BaseException:
   p.unlink(missing_ok=True)
   raise

 sys.stdout.buffer.write(b)

if __name__=='__main__':
 try:
  main()
 except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError,json.JSONDecodeError) as e:
  sys.exit('REJECTED: '+str(e))
