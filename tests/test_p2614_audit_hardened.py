import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "src" / "revisions" / "p2614_audit_hardened.py"
spec = importlib.util.spec_from_file_location("p2614_audit_hardened", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
audit_trades = module.audit_trades

def trade(**changes):
    x = dict(signal_i=1, entry_i=2, exit_i=3, edge_id="e1", capital_after=100, r=1, real_execution_allowed=False)
    x.update(changes)
    return x

class TestAudit(unittest.TestCase):
    def test_valid(self): self.assertTrue(audit_trades([trade()])["passed"])
    def test_missing(self): self.assertFalse(audit_trades([{}])["passed"])
    def test_bad_record(self): self.assertFalse(audit_trades([None])["passed"])
    def test_same_bar(self): self.assertFalse(audit_trades([trade(entry_i=1)])["passed"])
    def test_exit_order(self): self.assertFalse(audit_trades([trade(exit_i=2)])["passed"])
    def test_duplicate(self): self.assertFalse(audit_trades([trade(), trade()])["passed"])
    def test_real_execution(self): self.assertFalse(audit_trades([trade(real_execution_allowed=True)])["passed"])
    def test_missing_flag(self):
        t = trade(); del t["real_execution_allowed"]; self.assertFalse(audit_trades([t])["passed"])
    def test_nan(self): self.assertFalse(audit_trades([trade(r=float("nan"))])["passed"])
    def test_infinite_capital(self): self.assertFalse(audit_trades([trade(capital_after=float("inf"))])["passed"])
    def test_negative_capital(self): self.assertFalse(audit_trades([trade(capital_after=-1)])["passed"])
    def test_bad_indices(self): self.assertFalse(audit_trades([trade(signal_i=True)])["passed"])
    def test_empty_edge(self): self.assertFalse(audit_trades([trade(edge_id="")])["passed"])
    def test_empty(self): self.assertTrue(audit_trades([])["passed"])
