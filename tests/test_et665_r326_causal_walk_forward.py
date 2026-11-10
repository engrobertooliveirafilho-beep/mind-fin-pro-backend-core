"""ET665 R326 regression tests, offline."""
import csv
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
from mind_trader.research.et665_r326_causal_walk_forward import evaluate_csv

class WalkForwardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"trades.csv"
    def tearDown(self):
        self.tmp.cleanup()
    def rows(self,n=30):
        return [("e",(date(2025,1,1)+timedelta(days=i)).isoformat(),2 if i%3 else -1) for i in range(n)]
    def write(self,rows):
        with self.path.open("w",newline="") as fh:
            w=csv.writer(fh);w.writerow(["edge_id","timestamp","pnl_r"]);w.writerows(rows)
    def test_no_provenance(self):
        self.write(self.rows())
        self.assertEqual(evaluate_csv(self.path)["issues"],["CAUSAL_PROVENANCE_NOT_VERIFIED"])
    def test_empirical_metrics_research_only(self):
        self.write(self.rows())
        r=evaluate_csv(self.path,provenance_verified=True)
        self.assertEqual(r["edges"]["e"]["samples"],30)
        self.assertAlmostEqual(r["edges"]["e"]["pf"],4)
        self.assertFalse(r["runtime_promotion_allowed"])
    def test_order_rejected(self):
        a=self.rows();a[0],a[1]=a[1],a[0];self.write(a)
        self.assertIn("NONCHRONOLOGICAL_TRADES",evaluate_csv(self.path,provenance_verified=True)["issues"])
    def test_duplicate_rejected(self):
        a=self.rows();a.insert(1,a[0]);self.write(a)
        self.assertIn("DUPLICATE_EDGE_TIMESTAMP",evaluate_csv(self.path,provenance_verified=True)["issues"])
    def test_short_sample(self):
        self.write(self.rows(29))
        self.assertEqual(evaluate_csv(self.path,provenance_verified=True)["edges"]["e"]["decision"],"BLOCKED_INSUFFICIENT_SAMPLES")
    def test_nan_rejected(self):
        a=self.rows();a[0]=("e",a[0][1],"nan");self.write(a)
        self.assertIn("INVALID_TRADE",evaluate_csv(self.path,provenance_verified=True)["issues"])
    def test_bad_header(self):
        self.path.write_text("wrong,header\na,b\n")
        self.assertIn("INVALID_HEADER",evaluate_csv(self.path,provenance_verified=True)["issues"])
    def test_missing_file(self):
        self.assertIn("INVALID_SOURCE",evaluate_csv(self.path,provenance_verified=True)["issues"])

if __name__=="__main__":unittest.main()
