"""R516 offline contract regressions for the recovered RealDNA portfolio."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_module(name, relative_path):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

p2071 = load_module("r516_p2071", "app/runtime/p2071_2080_realtime_paper_runtime.py")
p2081 = load_module("r516_p2081", "app/runtime/p2081_2090_realtime_portfolio_governance.py")
p2091 = load_module("r516_p2091", "app/runtime/p2091_2100_realtime_intelligence_layer.py")

REALDNA = [
    {
        "specialist_id": "XAUUSD_M1_REALDNA_0004",
        "logic_type": "RANGE_REVERSION",
        "portfolio_weight": 0.5,
        "final_locked": True,
        "deployment_scope": "PAPER_ONLY_REAL_MARKET_DATA",
        "real_orders": "FORBIDDEN",
        "live_trading": False,
        "broker_execution": "DISABLED",
        "financial_execution": "DISABLED",
        "ftmo_real": "FORBIDDEN",
        "total_pnl": 1269.77,
        "max_drawdown": -0.01080484,
        "winrate": 0.527797,
    },
    {
        "specialist_id": "XAUUSD_M1_REALDNA_0003",
        "logic_type": "MEAN_REVERSION",
        "portfolio_weight": 0.249856,
        "final_locked": True,
        "deployment_scope": "PAPER_ONLY_REAL_MARKET_DATA",
        "real_orders": "FORBIDDEN",
        "live_trading": False,
        "broker_execution": "DISABLED",
        "financial_execution": "DISABLED",
        "ftmo_real": "FORBIDDEN",
        "total_pnl": 541.53,
        "max_drawdown": -0.00375963,
        "winrate": 0.540752,
    },
    {
        "specialist_id": "XAUUSD_M1_REALDNA_0001",
        "logic_type": "TREND_PULLBACK",
        "portfolio_weight": 0.164287,
        "final_locked": True,
        "deployment_scope": "PAPER_ONLY_REAL_MARKET_DATA",
        "real_orders": "FORBIDDEN",
        "live_trading": False,
        "broker_execution": "DISABLED",
        "financial_execution": "DISABLED",
        "ftmo_real": "FORBIDDEN",
        "total_pnl": 356.07,
        "max_drawdown": -0.00270735,
        "winrate": 0.522995,
    },
]

class TestRealDNAContract(unittest.TestCase):
    def write_portfolio(self, payload):
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
        json.dump(payload, tmp)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink, missing_ok=True)
        return tmp.name

    def test_original_three_specialists_load_without_fallback(self):
        path = self.write_portfolio(REALDNA)
        loaded = p2071.load_portfolio(path)
        self.assertEqual([x["specialist_id"] for x in loaded], [
            "XAUUSD_M1_REALDNA_0004",
            "XAUUSD_M1_REALDNA_0003",
            "XAUUSD_M1_REALDNA_0001",
        ])
        self.assertEqual([x["logic_type"] for x in loaded], [
            "RANGE_REVERSION", "MEAN_REVERSION", "TREND_PULLBACK"
        ])

    def test_invalid_portfolio_rejected_instead_of_fabricated_default(self):
        path = self.write_portfolio({"unexpected": []})
        with self.assertRaisesRegex(ValueError, "EXACTLY_3_SPECIALISTS"):
            p2071.load_portfolio(path)

    def test_unlocked_specialist_rejected(self):
        payload = json.loads(json.dumps(REALDNA))
        payload[1]["final_locked"] = False
        with self.assertRaisesRegex(ValueError, "NOT_LOCKED"):
            p2071.load_portfolio(self.write_portfolio(payload))

    def test_realDNA_unsupported_logic_fails_closed(self):
        with self.assertRaisesRegex(NotImplementedError, "REALDNA_LOGIC_NOT_RECOVERED"):
            p2071.SignalRuntime(REALDNA)

    def test_range_logic_is_explicitly_supported(self):
        engine = p2071.SignalRuntime([REALDNA[0]])
        self.assertEqual(engine.SUPPORTED_LOGIC_TYPES, {"RANGE_REVERSION"})

    def test_governance_extractor_rejects_missing_portfolio(self):
        with self.assertRaisesRegex(ValueError, "EXACTLY_3_SPECIALISTS"):
            p2081.extract_specialists({"unexpected": []})

    def test_intelligence_extractor_rejects_missing_portfolio(self):
        with self.assertRaisesRegex(ValueError, "EXACTLY_3_SPECIALISTS"):
            p2091.extract_specialists({"unexpected": []})

    def test_rebalancing_preserves_locked_weights_and_reserve(self):
        result = p2081.PortfolioRebalancing().evaluate(REALDNA)
        self.assertEqual(result.status, "PASS")
        self.assertAlmostEqual(result.payload["allocation_sum"], 0.914143, places=8)
        self.assertAlmostEqual(result.payload["cash_reserve_weight"], 0.085857, places=8)
        self.assertAlmostEqual(
            result.payload["allocation"]["XAUUSD_M1_REALDNA_0004"], 0.5, places=8
        )

    def test_capital_allocation_uses_weights_not_equal_thirds(self):
        result = p2081.CapitalAllocation().evaluate(REALDNA, 100000.0)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.payload["allocation"], {
            "XAUUSD_M1_REALDNA_0004": 50000.0,
            "XAUUSD_M1_REALDNA_0003": 24985.6,
            "XAUUSD_M1_REALDNA_0001": 16428.7,
        })
        self.assertEqual(result.payload["reserve_capital"], 8585.7)

    def test_risk_engine_enforces_p2067_three_percent_drawdown(self):
        result = p2081.RiskEngine().evaluate({
            "drawdown_pct": -0.031,
            "drawdown_abs": -3100.0,
            "daily_loss_pct": -0.005,
        })
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.payload["max_drawdown_pct"], -0.03)

    def test_risk_engine_fails_closed_without_daily_loss_metric(self):
        result = p2081.RiskEngine().evaluate({
            "drawdown_pct": -0.01,
            "drawdown_abs": -1000.0,
        })
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.reason, "DAILY_LOSS_METRIC_MISSING")

    def test_attribution_fails_closed_without_per_specialist_pnl(self):
        result = p2091.PerformanceAttribution().evaluate(
            REALDNA, {"metrics": {"paper_mark_to_market_pnl": -953.05}}
        )
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.reason, "SPECIALIST_ATTRIBUTION_MISSING_OR_INVALID")

    def test_attribution_requires_reconciled_specialist_values(self):
        result = p2091.PerformanceAttribution().evaluate(
            REALDNA,
            {"metrics": {
                "paper_mark_to_market_pnl": -100.0,
                "specialist_pnl": {
                    "XAUUSD_M1_REALDNA_0004": -50.0,
                    "XAUUSD_M1_REALDNA_0003": -30.0,
                    "XAUUSD_M1_REALDNA_0001": -20.0,
                },
            }},
        )
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.payload["attribution_sum"], -100.0)

    def test_ranking_uses_actual_historical_pnl_not_list_position(self):
        result = p2091.SpecialistRankingEvolution().evaluate(list(reversed(REALDNA)))
        self.assertEqual(result.status, "PASS")
        ranking = result.payload["ranking"]
        self.assertEqual(ranking[0]["specialist_id"], "XAUUSD_M1_REALDNA_0004")
        self.assertEqual(result.payload["ranking_basis"], "HISTORICAL_TOTAL_PNL")

if __name__ == "__main__":
    unittest.main()
