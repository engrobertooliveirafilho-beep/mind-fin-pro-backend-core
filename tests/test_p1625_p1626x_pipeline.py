import json, tempfile, unittest
from pathlib import Path
from app.runtime.p1625_p1626x_pipeline import run_file

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'edges.json'
        self.edges=[{'edge_id':'E1','profit_factor':2,'max_drawdown':0.2,'decay_revalidation_score':0.1},
                    {'edge_id':'E2','profit_factor':1.5,'max_drawdown':0.1,'decay_revalidation_score':0.2}]
    def execute(self):
        self.path.write_text(json.dumps(self.edges));return run_file(self.path)
    def test_valid(self):self.assertEqual(self.execute()['edges'],2)
    def test_no_orders(self):self.assertEqual(self.execute()['real_orders'],'FORBIDDEN')
    def test_no_e2e_claim(self):self.assertFalse(self.execute()['e2e_certified'])
    def test_hash(self):self.assertEqual(len(self.execute()['source_sha256']),64)
    def test_duplicate(self):
        self.edges[1]['edge_id']='E1'
        with self.assertRaises(ValueError):self.execute()
    def test_nan(self):
        self.edges[0]['profit_factor']=float('nan')
        with self.assertRaises(ValueError):self.execute()
    def test_inf(self):
        self.edges[0]['profit_factor']=float('inf')
        with self.assertRaises(ValueError):self.execute()
    def test_empty(self):
        self.edges=[]
        with self.assertRaises(ValueError):self.execute()
    def test_missing_file(self):
        with self.assertRaises(ValueError):run_file(self.path)
    def test_negative_drawdown(self):
        self.edges[0]['max_drawdown']=-0.1
        with self.assertRaises(ValueError):self.execute()
