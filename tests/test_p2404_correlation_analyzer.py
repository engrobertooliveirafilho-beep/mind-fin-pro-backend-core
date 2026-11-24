import unittest
from app.runtime.p2404_correlation_analyzer import (
    CorrelationInputError, analyze_correlation, pearson, spearman,
    overlap, drawdown_flags, runtime_allowed, safety_contract,
)

def rows_for(series):
    rows=[]
    for edge,values in series.items():
        for index,value in enumerate(values):
            rows.append({"edge_id":edge,"timestamp":f"2026-01-{index+1:02d}","pnl_r":value,
                "mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
                "real_execution_allowed":False})
    return rows

class P2404CorrelationTests(unittest.TestCase):
    def test_pearson_identical(self): self.assertAlmostEqual(pearson([1,2,3],[1,2,3]),1.0)
    def test_spearman_monotonic(self): self.assertAlmostEqual(spearman([1,2,3,4],[10,20,30,40]),1.0)
    def test_overlap_jaccard(self): self.assertAlmostEqual(overlap({"a":1,"b":2},{"b":3,"c":4}),1/3)
    def test_drawdown_flags(self): self.assertEqual(drawdown_flags([1,-2,1]),[0.0,1.0,1.0])
    def test_pairwise_count_and_redundancy(self):
        r=analyze_correlation(rows_for({"A":[1,2,3,4],"B":[1,2,3,4],"C":[4,3,2,1]}))
        self.assertEqual(r["pairwise_tests"],3); self.assertEqual(r["redundant_pairs"],3)
    def test_missing_timestamps_zero_fill_and_overlap(self):
        rows=[x for x in rows_for({"A":[1,2,3,4],"B":[1,2,3,4]})
              if not (x["edge_id"]=="B" and x["timestamp"]=="2026-01-02")]
        r=analyze_correlation(rows); pair=r["pairwise"][0]
        self.assertLess(pair["overlap"],1.0); self.assertEqual(r["timestamps"],4)
    def test_stats_drive_greedy_pool(self):
        rows=rows_for({"A":[1,2,3,4],"B":[1,2,3,4]})
        for day,value in ((2,-1),(4,1)):
            rows.append({"edge_id":"C","timestamp":f"2026-01-{day:02d}","pnl_r":value,
                "mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
                "real_execution_allowed":False})
        stats=[{"edge_id":e,"pf":2.0,"winrate":60,"expectancy":0.2,"net_r":10,
                "max_dd_r":2,"trades":220} for e in ("A","B","C")]
        r=analyze_correlation(rows,stats)
        self.assertEqual(len(r["selected_edges"]),2); self.assertEqual(set(r["selected_edges"]),{"A","C"})
    def test_duplicate_edge_timestamp_rejected(self):
        rows=rows_for({"A":[1,2,3],"B":[2,3,4]}); rows.append(dict(rows[0]))
        with self.assertRaises(CorrelationInputError): analyze_correlation(rows)
    def test_nan_rejected(self):
        rows=rows_for({"A":[1,2,3],"B":[2,3,4]}); rows[0]["pnl_r"]=float("nan")
        with self.assertRaises(CorrelationInputError): analyze_correlation(rows)
    def test_real_authority_rejected(self):
        rows=rows_for({"A":[1,2,3],"B":[2,3,4]}); rows[0]["real_execution_allowed"]=True
        with self.assertRaises(CorrelationInputError): analyze_correlation(rows)
    def test_invalid_threshold_rejected(self):
        with self.assertRaises(CorrelationInputError):
            analyze_correlation(rows_for({"A":[1,2,3],"B":[2,3,4]}),threshold=1.1)
    def test_runtime_never_authorized(self):
        self.assertFalse(runtime_allowed()); self.assertFalse(safety_contract()["runtime_allowed"])
        self.assertFalse(safety_contract()["real_execution_allowed"])

if __name__=="__main__": unittest.main()
