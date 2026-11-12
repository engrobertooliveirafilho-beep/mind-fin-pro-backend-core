import csv
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.backtest.p2405_paper_bridge import prepare_paper_candidates

class M7BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.csv = self.root / "bars.csv"
        self.db = self.root / "bars.sqlite"
        with self.csv.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["ts","open","high","low","close","volume"])
            w.writeheader()
            for i in range(120):
                price = 100 + (i // 12 % 2) * 8 + (i % 12) * (1 if i // 12 % 2 else -1)
                w.writerow({"ts":f"2026-01-01T{i//60:02d}:{i%60:02d}:00","open":price,"high":price+1,"low":price-1,"close":price,"volume":100})
        ingest_ohlcv_csv(str(self.csv),"EURUSD","M1",str(self.db))

    def bridge(self, **kwargs):
        return prepare_paper_candidates("EURUSD","M1",str(self.db),fast=3,slow=7,**kwargs)

    def test_next_bar_and_no_routing(self):
        result=self.bridge(spread=0.2,slippage=0.1,commission=0.5)
        self.assertEqual(result["decision"],"PAPER_CANDIDATES_NOT_AUTHORIZED_FOR_ROUTING")
        self.assertTrue(result["events"])
        for e in result["events"]:
            self.assertLess(e["signal_ts"],e["fill_ts"])
            self.assertEqual(e["decision"],"RESEARCH_ONLY_NOT_ROUTED")
            self.assertEqual(e["real_orders"],"FORBIDDEN")
            self.assertEqual(e["costs"]["commission"],0.5)

    def test_checkpoint_telemetry_immutable(self):
        checkpoint=self.root/"checkpoint.json"
        telemetry=self.root/"telemetry.json"
        self.bridge(checkpoint_path=checkpoint,telemetry_path=telemetry)
        self.assertTrue(checkpoint.exists() and telemetry.exists())
        with self.assertRaises(FileExistsError):
            self.bridge(checkpoint_path=checkpoint)

    def test_invalid_costs_fail_closed(self):
        for kwargs in ({"spread":-1},{"slippage":float("nan")},{"commission":float("inf")}):
            with self.assertRaises(ValueError):
                self.bridge(**kwargs)

    def test_deterministic_candidates(self):
        a=self.bridge()
        b=self.bridge()
        self.assertEqual(a["events"],b["events"])

if __name__ == "__main__":
    unittest.main()
