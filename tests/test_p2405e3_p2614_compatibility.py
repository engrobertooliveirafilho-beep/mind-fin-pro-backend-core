import importlib.util
import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bridge", ROOT/"src"/"revisions"/"p2405e3_p2614_compatibility.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
def c(**kwargs):
    v = dict(edge_id="E",family="ATR",pattern="ATR_BREAKOUT",session="EU_MORNING",regime="TREND_UP",timeframe="M15",direction="BUY_PAPER",risk_model="ATR_STOP_1_2",filter="ATR_FILTER",mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",real_execution_allowed=False)
    v.update(kwargs);return v
class TestBridge(unittest.TestCase):
    def test_historical_candidate_rejected(self): self.assertFalse(mod.audit_candidate(c())["compatible"])
    def test_unsupported_risk(self): self.assertIn("UNSUPPORTED_RISK_MODEL",mod.audit_candidate(c())["reasons"])
    def test_unsupported_pattern(self): self.assertIn("UNIMPLEMENTED_PATTERN_OR_FILTER",mod.audit_candidate(c())["reasons"])
    def test_real_flag(self): self.assertIn("PAPER_GOVERNANCE_FAILURE",mod.audit_candidate(c(real_execution_allowed=True))["reasons"])
    def test_real_direction(self): self.assertIn("INVALID_DIRECTION",mod.audit_candidate(c(direction="BUY_REAL"))["reasons"])
    def test_bad_record(self): self.assertFalse(mod.audit_candidate(None)["compatible"])
    def test_missing(self): self.assertFalse(mod.audit_candidate({})["compatible"])
    def test_no_promotion(self):
        x=mod.audit_candidate(c(pattern="NO_PATTERN",filter="NO_FILTER",risk_model="ATR_STOP"))
        self.assertTrue(x["compatible"]);self.assertFalse(x["runtime_allowed"])
    def test_unsupported_family(self): self.assertIn("UNSUPPORTED_FAMILY",mod.audit_candidate(c(family="VWAP"))["reasons"])
