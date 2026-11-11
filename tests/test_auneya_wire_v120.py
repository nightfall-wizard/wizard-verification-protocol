import copy,hashlib,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tests'),str(R/'tools/auneya')]
import test_auneya_quorum_v111 as source
import auneya_capsule_v112 as cap
import auneya_peer_gate_v16 as canon
import auneya_wire_v120 as wire
class WireTests(unittest.TestCase):
    def setUp(self):
        b=source.MultiKeeperTests('test_authenticated_quorum_and_determinism')
        b.setUp();self.addCleanup(b.doCleanups)
        self.b=b;self.f=b.root/'wire120.json'
        cap.export_capsule(b.trust,b.b1,self.f)
        self.digest=hashlib.sha256(self.f.read_bytes()).hexdigest()
    def test_signed_and_mutations(self):
        self.assertEqual(wire.profile(self.f)[0],self.f.read_bytes())
        out=wire.baseline.decode(
            wire.build(str(self.b.trust),str(self.f),self.digest),65536)
        self.assertEqual(out['negative_vectors_passed'],15)
        self.assertFalse(out['independent_devices_proven'])
        self.assertFalse(out['economic_activation'])
        original=cap.strict_bytes(self.f.read_bytes())
        changes=(lambda x:x.update(unknown=True),
                 lambda x:x.update(sequence=True),
                 lambda x:x.update(sequence=2**63),
                 lambda x:x['current'].update(receipts=[]))
        invalid=self.b.root/'invalid.json'
        for change in changes:
            x=copy.deepcopy(original);change(x)
            invalid.write_bytes(canon.canonical(x)+b'\n')
            with self.assertRaises(ValueError):wire.profile(invalid)
        with self.assertRaises(ValueError):
            wire.build(str(self.b.trust),str(self.f),'0'*64)
