import tempfile
import unittest
from pathlib import Path
from tools.audit_trader_stubs import scan

class InventoryTests(unittest.TestCase):
    def test_detects_pass_and_not_implemented(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'mind_trader_stub.py'
            p.write_text('def a():\n    pass\ndef b():\n    raise NotImplementedError()\n')
            rows=scan(root)['items']
            self.assertEqual(len(rows),1)
            self.assertEqual({h['reason'] for h in rows[0]['hits']},{'PASS_ONLY','NOT_IMPLEMENTED'})
    def test_does_not_flag_functional_code(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'mind_trader_real.py').write_text('def a(x):\n    return x+1\n')
            self.assertEqual(scan(root)['items'],[])
    def test_does_not_certify_replacements(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(scan(Path(d))['merge_allowed'])
            self.assertEqual(scan(Path(d))['certified_replacements'],0)

if __name__=='__main__':unittest.main()
