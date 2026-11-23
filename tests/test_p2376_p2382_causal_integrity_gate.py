import unittest
from app.runtime.p2376_p2382_causal_integrity_gate import CausalIntegrityError, apply_training_blocks, deterministic_signal_id, next_executable_candle_index, summarize_replay, validate_decision_payload
class CausalGateTests(unittest.TestCase):
 def test_01_reject_post_mfe_feature(self):
  with self.assertRaises(CausalIntegrityError): validate_decision_payload({"post_mfe_atr":1.2})
 def test_02_reject_post_mae_feature(self):
  with self.assertRaises(CausalIntegrityError): validate_decision_payload({"post_mae_atr":0.8})
 def test_03_reject_post_efficiency_feature(self):
  with self.assertRaises(CausalIntegrityError): validate_decision_payload({"post_efficiency":2.0})
 def test_04_allow_past_current_features(self): validate_decision_payload({"atr14":1.1,"rsi14":52,"tick_volume_ratio_50":1.4})
 def test_05_outcome_separate_from_decision_payload(self):
  validate_decision_payload({"atr14":1.1}); self.assertEqual({"post_mfe_atr":1.2}["post_mfe_atr"],1.2)
 def test_06_entry_first_strictly_later_candle(self):
  s={"symbol":"DE40","event_time":"2026-11-23T10:00:00Z"}; c=[{"symbol":"DE40","time":"2026-11-23T10:00:00Z"},{"symbol":"DE40","time":"2026-11-23T10:15:00Z"},{"symbol":"DE40","time":"2026-11-23T10:30:00Z"}]; self.assertEqual(next_executable_candle_index(signal=s,candles=c),1)
 def test_07_reject_timezone_naive_signal(self):
  with self.assertRaises(CausalIntegrityError): next_executable_candle_index(signal={"symbol":"DE40","event_time":"2026-11-23T10:00:00"},candles=[{"symbol":"DE40","time":"2026-11-23T10:15:00Z"}])
 def test_08_reject_symbol_mismatch(self):
  with self.assertRaises(CausalIntegrityError): next_executable_candle_index(signal={"symbol":"DE40","event_time":"2026-11-23T10:00:00Z"},candles=[{"symbol":"GER40","time":"2026-11-23T10:15:00Z"}])
 def test_09_reject_unsorted_or_duplicate_candles(self):
  with self.assertRaises(CausalIntegrityError): next_executable_candle_index(signal={"symbol":"DE40","event_time":"2026-11-23T10:00:00Z"},candles=[{"symbol":"DE40","time":"2026-11-23T10:30:00Z"},{"symbol":"DE40","time":"2026-11-23T10:15:00Z"}])
 def test_10_signal_id_stable(self):
  a=dict(symbol="DE40",timeframe="M15",event_time="2026-11-23T10:00:00Z",family="BREAKOUT",source_row_sha256="a"*64); self.assertEqual(deterministic_signal_id(**a),deterministic_signal_id(**a))
 def test_11_loss_rows_not_removed(self):
  rows=[{"family":"BREAKOUT","timeframe":"M15","realized_r":1.0},{"family":"BREAKOUT","timeframe":"M15","realized_r":-1.0}]; kept=apply_training_blocks(rows,set()); self.assertEqual(len(kept),2); self.assertEqual(sum(x["realized_r"]<0 for x in kept),1)
 def test_12_only_train_blocked_family_tf_removed(self):
  rows=[{"family":"BREAKOUT","timeframe":"M15","realized_r":-1},{"family":"PULLBACK","timeframe":"M15","realized_r":-1}]; kept=apply_training_blocks(rows,{("BREAKOUT","M15")}); self.assertEqual([x["family"] for x in kept],["PULLBACK"])
 def test_13_no_loss_pf_not_999(self):
  summary=summarize_replay([{"realized_r":1.0},{"realized_r":2.0}]); self.assertIsNone(summary["profit_factor"]); self.assertEqual(summary["losses"],0)
 def test_14_full_population_included(self):
  summary=summarize_replay([{"realized_r":1.0},{"realized_r":-1.0},{"realized_r":0.0}]); self.assertEqual((summary["samples"],summary["wins"],summary["losses"]),(3,1,1)); self.assertTrue(summary["all_rows_included"])
if __name__=="__main__": unittest.main()
