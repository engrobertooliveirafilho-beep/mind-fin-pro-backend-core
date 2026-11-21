import unittest
from unittest.mock import patch
from app.runtime.p2223_broker_emulator import BrokerEmulator, RiskEngine, run_simulation

class BrokerEmulatorSafetyTests(unittest.TestCase):
    def test_reject_unknown_side(self):
        b=BrokerEmulator()
        with self.assertRaises(ValueError): b.execute_order("HOLD",1)
        self.assertEqual(len(b.trades),0)
    def test_reject_zero_volume(self):
        b=BrokerEmulator()
        with self.assertRaises(ValueError): b.execute_order("BUY",0)
    def test_reject_nan_volume(self):
        b=BrokerEmulator()
        with self.assertRaises(ValueError): b.execute_order("SELL",float("nan"))
    def test_reject_boolean_volume(self):
        b=BrokerEmulator()
        with self.assertRaises(ValueError): b.execute_order("BUY",True)
    def test_session_loss_kill_is_sticky(self):
        r=RiskEngine()
        self.assertEqual(r.check(-3100),"KILLED")
        self.assertEqual(r.check(10000),"KILLED")
        self.assertEqual(r.equity,96900)
    def test_drawdown_kill_is_sticky(self):
        r=RiskEngine()
        self.assertEqual(r.check(10000),"OK")
        self.assertEqual(r.check(-6000),"KILLED")
        self.assertEqual(r.check(1),"KILLED")
    def test_reject_order_after_kill(self):
        b=BrokerEmulator()
        b.risk.check(-3100)
        with self.assertRaises(RuntimeError): b.execute_order("BUY",1)
        self.assertEqual(b.trades,[])
    def test_reject_nonfinite_pnl(self):
        r=RiskEngine()
        with self.assertRaises(ValueError): r.check(float("inf"))
        self.assertEqual(r.equity,100000)
    def test_simulation_is_not_certification(self):
        with patch("app.runtime.p2223_broker_emulator.random.uniform",return_value=0):
            r=run_simulation(cycles=1)
        self.assertEqual(r["status"],"SIMULATED")
        self.assertEqual(r["total_trades"],1)
    def test_reject_insolvent_equity(self):
        r=RiskEngine()
        self.assertEqual(r.check(-100000),"KILLED")
        self.assertTrue(r.killed)
        self.assertEqual(r.equity,100000)
    def test_reject_overflowed_equity(self):
        r=RiskEngine()
        self.assertEqual(r.check(1e308),"OK")
        self.assertEqual(r.check(1e308),"KILLED")
        self.assertTrue(r.killed)
        self.assertTrue(__import__("math").isfinite(r.equity))
