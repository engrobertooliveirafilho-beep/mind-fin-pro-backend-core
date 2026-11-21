import importlib.util
import pathlib
import unittest
p=pathlib.Path(__file__).resolve().parents[1]/"src"/"revisions"/"p2405f_evidence_gate.py"
spec=importlib.util.spec_from_file_location("gate",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
G=dict(mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",real_execution_allowed=False,decision="PROMOTE_IDEAL",pf=3,winrate=56,expectancy=.04,max_dd_r=3,samples=105,passed_windows=4)
class Gate(unittest.TestCase):
    def test_historical_blocked(self): self.assertFalse(m.audit_p2405f_promotion(G)["certified"])
    def test_no_runtime(self): self.assertFalse(m.audit_p2405f_promotion(G)["runtime_allowed"])
    def test_missing_trades(self): self.assertIn("MISSING_VERIFIED_TRADES",m.audit_p2405f_promotion(G)["reasons"])
    def test_missing_windows(self): self.assertIn("MISSING_VERIFIED_WINDOWS",m.audit_p2405f_promotion(G)["reasons"])
    def test_not_recomputed(self): self.assertIn("METRICS_NOT_RECOMPUTED",m.audit_p2405f_promotion(G,[1],[1])["reasons"])
    def test_real_block(self): self.assertIn("GOVERNANCE_FAILURE",m.audit_p2405f_promotion(dict(G,mode="REAL"))["reasons"])
    def test_nan(self): self.assertIn("INVALID_PF",m.audit_p2405f_promotion(dict(G,pf=float("nan")))["reasons"])
    def test_missing(self): self.assertIn("INVALID_PF",m.audit_p2405f_promotion({})["reasons"])
    def test_invalid(self): self.assertFalse(m.audit_p2405f_promotion(None)["certified"])
    def test_reject(self): self.assertIn("NOT_PROMOTED",m.audit_p2405f_promotion(dict(G,decision="REJECT"))["reasons"])
