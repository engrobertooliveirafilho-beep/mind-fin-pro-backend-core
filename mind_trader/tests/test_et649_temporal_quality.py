import csv
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.data.ingestion_adapters import quality_report, normalize_csv

class TemporalQualityGateTests(unittest.TestCase):
    def report(self, timestamps, ohlc=None):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"prices.csv"
            with p.open("w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(("ts","open","high","low","close","volume"))
                for i,ts in enumerate(timestamps):
                    w.writerow((ts,*(ohlc or (1,3,0,2)),10))
            return quality_report(p,min_rows=2)

    def test_valid_utc(self):
        self.assertEqual(self.report(["2026-01-01T00:00:00Z","2026-01-01T01:00:00+00:00"])["decision"],"ALLOW_BACKTEST")

    def test_reverse_order_blocks(self):
        r=self.report(["2026-01-01T01:00:00Z","2026-01-01T00:00:00Z"])
        self.assertEqual(r["ordering_issues"],1)
        self.assertEqual(r["decision"],"BLOCK_BACKTEST")

    def test_duplicate_equivalent_utc_blocks(self):
        r=self.report(["2026-01-01T00:00:00Z","2026-01-01T00:00:00+00:00"])
        self.assertEqual(r["duplicates"],1)
        self.assertEqual(r["decision"],"BLOCK_BACKTEST")

    def test_naive_timestamp_blocks(self):
        self.assertEqual(self.report(["2026-01-01 00:00:00","2026-01-01T01:00:00Z"])["invalid_timestamps"],1)

    def test_non_utc_offset_blocks(self):
        self.assertEqual(self.report(["2026-01-01T00:00:00+03:00","2026-01-01T01:00:00Z"])["decision"],"BLOCK_BACKTEST")

    def test_invalid_ohlc_blocks(self):
        self.assertEqual(self.report(["2026-01-01T00:00:00Z","2026-01-01T01:00:00Z"],(1,0,2,1))["decision"],"BLOCK_BACKTEST")

    def test_nan_blocks(self):
        self.assertEqual(self.report(["2026-01-01T00:00:00Z","2026-01-01T01:00:00Z"],(float("nan"),3,0,2))["decision"],"BLOCK_BACKTEST")

    def test_timestamp_alias_normalizes(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"source.csv"; dest=Path(d)/"normalized.csv"
            source.write_text("timestamp,open,high,low,close,volume\n2026-01-01T00:00:00Z,1,3,0,2,10\n",encoding="utf-8")
            normalize_csv(source,dest)
            self.assertIn("+00:00",dest.read_text())

if __name__=="__main__": unittest.main()
