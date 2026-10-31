import unittest
from app.runtime.p2223_broker_emulator import RiskEngine

class TestRiskLatchIsolation(unittest.TestCase):
    def test_global_kill_survives_day_reset(self):
        risk = RiskEngine()
        self.assertEqual(risk.check(-5000), "KILLED")
        self.assertTrue(risk.global_killed)
        risk.reset_day()
        self.assertEqual(risk.check(10000), "KILLED")
        self.assertEqual(risk.equity, 95000)

    def test_daily_kill_resets_without_global_kill(self):
        risk = RiskEngine()
        self.assertEqual(risk.check(-3000), "KILLED")
        self.assertTrue(risk.daily_killed)
        self.assertFalse(risk.global_killed)
        risk.reset_day()
        self.assertFalse(risk.daily_killed)
        self.assertEqual(risk.check(0), "OK")

    def test_global_kill_does_not_reset_peak(self):
        risk = RiskEngine()
        risk.check(-5000)
        original_peak = risk.peak
        risk.reset_day()
        self.assertEqual(risk.peak, original_peak)
        self.assertTrue(risk.global_killed)

if __name__ == "__main__":
    unittest.main()
