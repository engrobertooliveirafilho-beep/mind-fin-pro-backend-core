import importlib.util
import pathlib
import unittest
from datetime import datetime, timedelta
MODULE = pathlib.Path(__file__).resolve().parents[1] / "src" / "revisions" / "p2614_replay_chronological.py"
spec = importlib.util.spec_from_file_location("p2614_replay_chronological", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
replay = module.replay_chronological
C = [{"time":datetime(2026,1,1)+timedelta(hours=i)} for i in range(100)]
E = [{"edge_id":"a","direction":"BUY_PAPER"}]
def fill(edge,candles,features,i):
    return {"entry_i":i+1,"exit_i":i+5,"r":1.,"real_execution_allowed":False} if i in (60,61,65) else None
class TestReplay(unittest.TestCase):
    def test_no_overlap(self):
        s,curve,trades=replay(E,C,{},fill)
        self.assertEqual(len(trades),2)
        self.assertEqual([t["entry_i"] for t in trades],[61,66])
    def test_settlement_not_signal(self):
        _,curve,trades=replay(E,C,{},fill)
        self.assertEqual(curve[0]["capital"],100)
        self.assertEqual(curve[4]["capital"],100)
        self.assertGreater(curve[5]["capital"],100)
    def test_daily_limit(self): self.assertEqual(replay(E,C,{},fill,max_trades_per_day=1)[0]["trades"],1)
    def test_invalid_risk(self):
        with self.assertRaises(ValueError): replay(E,C,{},fill,risk_pct=2)
    def test_invalid_capital(self):
        with self.assertRaises(ValueError): replay(E,C,{},fill,initial_capital=0)
    def test_invalid_direction(self):
        with self.assertRaises(ValueError): replay([{"edge_id":"a","direction":"BUY_REAL"}],C,{},fill)
    def test_duplicate_edge(self):
        with self.assertRaises(ValueError): replay(E+E,C,{},fill)
    def test_real_flag(self):
        def bad(*args): return dict(fill(*args),real_execution_allowed=True) if fill(*args) else None
        with self.assertRaises(ValueError): replay(E,C,{},bad)
    def test_nonfinite_r(self):
        def bad(*args): return dict(fill(*args),r=float("nan")) if fill(*args) else None
        with self.assertRaises(ValueError): replay(E,C,{},bad)
    def test_invalid_exit(self):
        def bad(*args): return dict(fill(*args),exit_i=args[3]) if fill(*args) else None
        with self.assertRaises(ValueError): replay(E,C,{},bad)
    def test_paper_output(self): self.assertIs(replay(E,C,{},fill)[0]["real_execution_allowed"],False)
