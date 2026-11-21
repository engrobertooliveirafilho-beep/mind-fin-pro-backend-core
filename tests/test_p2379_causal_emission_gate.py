import csv
import tempfile
import unittest
from pathlib import Path
from app.runtime.p2379_de40_forward_paper_emission_from_promoted_playbooks import create_signal, run


class P2379CausalEmissionGateTests(unittest.TestCase):
    def test_historical_promoted_row_never_emits_ready(self):
        row = {"timeframe": "M5", "regime": "TREND_UP", "footprint": "DISPLACEMENT_UP",
               "samples": 1000, "profit_factor_proxy": 5, "expectancy_r_proxy": 2,
               "max_drawdown_r_proxy": 1, "avg_rr_possible_proxy": 5}
        result = create_signal(row, "PLAYBOOK", 1)
        self.assertEqual(result["signal_status"], "PAPER_OBSERVE_ONLY")
        self.assertEqual(result["execution_permission"], "DENIED_PENDING_CAUSAL_REPLAY")
        self.assertEqual(result["real_orders"], "FORBIDDEN")

    def test_run_never_writes_ready_bus_from_historical_rows(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            files = [root / x for x in ("playbooks.csv", "contexts.csv", "sequences.csv")]
            for path in files:
                with path.open("w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["timeframe", "regime", "footprint", "samples",
                                                           "profit_factor_proxy", "expectancy_r_proxy",
                                                           "max_drawdown_r_proxy"])
                    writer.writeheader()
                    writer.writerow({"timeframe": "M5", "regime": "TREND_UP", "footprint": "DISPLACEMENT_UP",
                                     "samples": 100, "profit_factor_proxy": 3, "expectancy_r_proxy": 1,
                                     "max_drawdown_r_proxy": 1})
            out = run(*files, root / "out")
            self.assertEqual(out["paper_signals_total"], 3)
            self.assertEqual(out["paper_signals_ready"], 0)
            self.assertEqual(out["paper_signal_bus_rows"], 0)
            self.assertEqual(out["certification"], "NOT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()
