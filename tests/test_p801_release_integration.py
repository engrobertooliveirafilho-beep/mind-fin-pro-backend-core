import json,os,unittest
from pathlib import Path
from app.runtime.p801_release_interlock import release_gate

class TestP801Integration(unittest.TestCase):
    @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'historical Drive exports required')
    def test_historical_release_blocked(self):
        root=Path(os.environ['ELDORA_HISTORICAL_DIR'])
        def read(name):return json.loads((root/name).read_text(encoding='utf-8'))
        out=release_gate(read('p601_700_allocation.json'),read('p601_700_master_report.json'),read('p701_supervised_edges.json'),read('p801_release_gate.json'))
        self.assertEqual(out['certification'],'BLOCKED_RISK')
        self.assertFalse(out['demo_operation_ready'])
        self.assertFalse(out['real_ftmo_release_allowed'])
        self.assertFalse(out['e2e_certified'])
