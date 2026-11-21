import math, unittest
from mind_trader.research.p2286d_costed_replay import replay

def row(t,close,trend="UP"):
    return {"time":f"2026-01-01 00:{t:02d}:00","open":float(close),"close":float(close),
      "sma_9":float(close)-1 if trend=="UP" else float(close)+1,"sma_21":1.0,"sma_55":1.0,"sma_200":1.0,"atr_pct":0.1,
      "session":"NY","volatility_state":"NORMAL","spread_state":"LOW","trend_9_21":trend,"trend_21_55":trend,"trend_55_200":trend}

class ReplayTests(unittest.TestCase):
    def test_requires_explicit_cost(self):
        with self.assertRaisesRegex(ValueError,"EXPLICIT_NONNEGATIVE_COST"): replay([row(0,100),row(1,101),row(2,102)])
    def test_rejects_negative_cost(self):
        with self.assertRaisesRegex(ValueError,"EXPLICIT_NONNEGATIVE_COST"): replay([row(0,100),row(1,101),row(2,102)],cost_per_side=-.1)
    def test_rejects_nonfinite_cost(self):
        with self.assertRaisesRegex(ValueError,"EXPLICIT_NONNEGATIVE_COST"): replay([row(0,100),row(1,101),row(2,102)],cost_per_side=math.nan)
    def test_same_side_signal_does_not_reset_entry(self):
        out=replay([row(0,100),row(1,102),row(2,104),row(3,106)],cost_per_side=0)
        self.assertEqual(out["trades"],1); self.assertEqual(out["trades_ledger"][0]["entry_price"],102.0)
    def test_terminal_position_is_closed(self):
        out=replay([row(0,100),row(1,102),row(2,105)],cost_per_side=0)
        self.assertTrue(out["terminal_position_closed"]); self.assertEqual(out["trades_ledger"][-1]["exit_reason"],"TERMINAL_CLOSE")
        self.assertEqual(out["trades_ledger"][-1]["exit_price"],105.0)
    def test_cost_is_charged_on_both_sides(self):
        out=replay([row(0,100),row(1,102),row(2,105)],cost_per_side=.5); t=out["trades_ledger"][0]
        self.assertEqual(t["gross_pnl"],3.0); self.assertEqual(t["net_pnl"],2.0); self.assertEqual(out["total_cost_price_units"],1.0)
    def test_opposite_signal_closes_and_reverses_next_open(self):
        out=replay([row(0,100),row(1,102),row(2,105,"DOWN"),row(3,103,"DOWN")],cost_per_side=0)
        self.assertEqual(out["trades"],2); self.assertEqual(out["trades_ledger"][0]["exit_reason"],"OPPOSITE_SIGNAL")
        self.assertEqual(out["trades_ledger"][0]["exit_price"],103.0); self.assertEqual(out["trades_ledger"][1]["side"],"SELL")
    def test_unsupported_strategy_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_STRATEGY"): replay([row(0,100),row(1,101),row(2,102)],cost_per_side=0,strategy="MAGIC")
if __name__=="__main__": unittest.main(verbosity=2)
