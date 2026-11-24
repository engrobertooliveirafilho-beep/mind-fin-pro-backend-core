import unittest
from app.runtime.p2404_correlation_analyzer import CorrelationInputError, analyze_correlation, runtime_allowed, safety_contract

def make_rows():
    rows = []
    for i in range(30):
        stamp = f"2026-01-{i+1:02d}T00:00:00"
        for edge, value in (("A", float(i-10)), ("B", float(i-10)), ("C", float(10-i)), ("D", float((i%3)-1))):
            rows.append({"edge_id":edge,"timestamp":stamp,"signal":"BUY","pnl_r":value,
                         "entry_time":stamp,"exit_time":stamp.replace("00:00:00","00:05:00"),"holding_bars":1})
    return rows

class P2404CorrelationTests(unittest.TestCase):
    def test_identical_series_detected_as_redundant(self):
        r=analyze_correlation([x for x in make_rows() if x["edge_id"] in ("A","B")])
        self.assertEqual(r["status"],"MEASURED"); self.assertEqual(r["redundant_pairs"],1)
        self.assertAlmostEqual(r["pair_results"][0]["correlation"],1.0)
    def test_inverse_series_detected_by_absolute_correlation(self):
        r=analyze_correlation([x for x in make_rows() if x["edge_id"] in ("A","C")])
        self.assertEqual(r["redundant_pairs"],1); self.assertAlmostEqual(r["pair_results"][0]["correlation"],-1.0)
    def test_unrelated_series_measured(self):
        r=analyze_correlation([x for x in make_rows() if x["edge_id"] in ("A","D")])
        self.assertEqual(r["status"],"MEASURED"); self.assertEqual(r["pairs"],1)
    def test_insufficient_overlap_is_not_zero_filled(self):
        rows=[x for x in make_rows() if x["edge_id"] in ("A","B") and (x["edge_id"]=="A" or int(x["timestamp"][8:10])<=10)]
        r=analyze_correlation(rows,min_overlap=20)
        self.assertEqual(r["status"],"INCOMPLETE"); self.assertEqual(r["unmeasured_pairs"],1)
        self.assertIsNone(r["pair_results"][0]["correlation"])
    def test_duplicate_edge_timestamp_fails_closed(self):
        rows=make_rows(); rows.append(dict(rows[0]))
        with self.assertRaises(CorrelationInputError): analyze_correlation(rows)
    def test_nan_pnl_fails_closed(self):
        rows=make_rows(); rows[0]["pnl_r"]=float("nan")
        with self.assertRaises(CorrelationInputError): analyze_correlation(rows)
    def test_boolean_pnl_fails_closed(self):
        rows=make_rows(); rows[0]["pnl_r"]=True
        with self.assertRaises(CorrelationInputError): analyze_correlation(rows)
    def test_constant_series_is_unmeasured(self):
        rows=make_rows()
        for x in rows:
            if x["edge_id"]=="B": x["pnl_r"]=1.0
        r=analyze_correlation([x for x in rows if x["edge_id"] in ("A","B")])
        self.assertEqual(r["status"],"INCOMPLETE"); self.assertEqual(r["unmeasured_pairs"],1)
    def test_missing_required_field_fails_closed(self):
        row=dict(make_rows()[0]); del row["exit_time"]
        with self.assertRaises(CorrelationInputError): analyze_correlation([row,dict(make_rows()[-1])])
    def test_invalid_threshold_fails_closed(self):
        with self.assertRaises(CorrelationInputError): analyze_correlation(make_rows(),threshold=1.5)
    def test_invalid_min_overlap_fails_closed(self):
        with self.assertRaises(CorrelationInputError): analyze_correlation(make_rows(),min_overlap=True)
    def test_runtime_is_never_authorized(self):
        self.assertFalse(runtime_allowed()); self.assertFalse(safety_contract()["runtime_allowed"])
        self.assertFalse(safety_contract()["real_execution_allowed"])

if __name__ == "__main__":
    unittest.main()
