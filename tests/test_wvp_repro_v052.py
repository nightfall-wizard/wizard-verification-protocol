import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tools/wvp_repro_v052.py'
s=importlib.util.spec_from_file_location('wvp052',p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

class TestContract(unittest.TestCase):
 def test_canonical(self):
  x={'format':'wvp-local-v1','claims':dict(m.FALSE)}
  self.assertEqual(m.decode(m.canonical(x)),x)

 def test_forged_claim(self):
  x={'format':'wvp-local-v1','claims':dict(m.FALSE,audit=True)}
  with self.assertRaises(ValueError):
   m.decode(m.canonical(x))

 def test_duplicate(self):
  with self.assertRaises(ValueError):
   m.decode(b'{"format":"wvp-local-v1","format":"wvp-local-v1","claims":{}}\n')
