import tempfile, unittest
from pathlib import Path
from p2500_inventory import inspect_source
from p2501_gate import review
from p2502_staging_guard import stage
class Integration(unittest.TestCase):
    def test_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'source'; root.mkdir(); dest=Path(tmp)/'stage'
            raw=b'from . import helper\nimport os, sys\n'; p=root/'motor.py'; p.write_bytes(raw)
            inv=inspect_source(raw); self.assertEqual(inv['imports'],['.','os','sys'])
            gate=review(raw,inv); self.assertEqual(gate['action'],'TEST_CANDIDATE')
            self.assertFalse(gate['promotion_allowed'])
            result=stage(root,dest,'motor.py',gate['sha256']); self.assertFalse(result['runtime_active']); self.assertEqual((dest/'motor.py').read_bytes(),raw)
            self.assertEqual(review(raw,inv,True)['action'],'REVIEW_OR_QUARANTINE')
            p.write_bytes(b'changed=1'); self.assertEqual(review(p.read_bytes(),inv)['action'],'REVIEW_OR_QUARANTINE')
            with self.assertRaises(ValueError): stage(root,dest,'motor.py',gate['sha256'])
            self.assertEqual((dest/'motor.py').read_bytes(),raw)
if __name__=='__main__': unittest.main()
