import unittest
from p2377_causal_gate import audit_text
SOURCE='''def context_window(candles,event,before=20,after=20):
 post=candles[i+1:min(len(candles),i+after+1)]
 return {"post_mfe_atr":mfe,"post_mae_atr":mae,"post_efficiency":eff,"post_followthrough":follow}
def classify_lifecycle(event,context):
 post_mfe=context.get("post_mfe_atr")
 post_mae=context.get("post_mae_atr")
 efficiency=context.get("post_efficiency")
 follow=context.get("post_followthrough")
 return post_mfe
def context_score(regime_score,lifecycle_score,event,context):
 efficiency=context.get("post_efficiency")
 return regime_score+efficiency
'''
SAFE='''def classify_lifecycle(event,context):
 return event.get("event_type")
def context_score(regime_score,lifecycle_score,event,context):
 return regime_score+lifecycle_score
'''
class Tests(unittest.TestCase):
 def test_detects_future_lifecycle_inputs(self):
  r=audit_text(SOURCE);self.assertTrue(r["lifecycle_uses_future_outcomes"])
 def test_detects_future_score_inputs(self):
  self.assertTrue(audit_text(SOURCE)["context_score_uses_future_outcomes"])
 def test_future_window_detected(self):
  self.assertTrue(audit_text(SOURCE)["future_window_generated"])
 def test_lookahead_blocks_causal_certification(self):
  r=audit_text(SOURCE);self.assertTrue(r["lookahead_bias_detected"]);self.assertFalse(r["causal_signal_certified"])
 def test_safe_contract_has_no_lookahead(self):
  self.assertFalse(audit_text(SAFE)["lookahead_bias_detected"])
if __name__=="__main__":unittest.main()
