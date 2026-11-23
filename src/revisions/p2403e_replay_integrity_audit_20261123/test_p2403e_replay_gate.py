import tempfile,unittest
from pathlib import Path
from p2403e_replay_gate import validate
SRC='''import hashlib
seed=int(hashlib.sha256((edge_id+"|DE40|M15").encode()).hexdigest()[:8],16)
stride=5+(seed%19); offset=seed%stride; hold=2+(seed%10)
for i in range(offset,len(candles)-hold-1,stride):
 entry=candles[i]; exitr=candles[i+hold]
 raw=(exitr["close"]-entry["close"])/entry["close"]
 pnl_r=raw*entry["close"]/atr
'''
class Tests(unittest.TestCase):
 def run_gate(self):
  f=tempfile.NamedTemporaryFile("w",suffix=".py",delete=False);f.write(SRC);f.close();p=Path(f.name)
  try:return validate(p)
  finally:p.unlink()
 def test_hash_schedule_detected(self):self.assertTrue(self.run_gate()["hash_based_trade_schedule"])
 def test_no_strategy_signals(self):self.assertFalse(self.run_gate()["strategy_signal_rules_present"])
 def test_no_cost_model(self):self.assertFalse(self.run_gate()["transaction_cost_model_present"])
 def test_not_valid_replay(self):
  r=self.run_gate();self.assertTrue(r["pseudo_replay_detected"]);self.assertFalse(r["trade_rows_are_strategy_replay"])
 def test_correlation_and_promotion_blocked(self):
  r=self.run_gate();self.assertFalse(r["correlation_ready"]);self.assertFalse(r["runtime_promotion_allowed"])
if __name__=="__main__":unittest.main()
