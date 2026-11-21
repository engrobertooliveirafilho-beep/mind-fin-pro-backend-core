import unittest
from app.runtime.p2378_de40_router_backtest_sequence_playbook_promotion_gate import build_playbooks


class P2378DeterminismTests(unittest.TestCase):
    def test_playbook_id_is_stable_across_repeated_builds(self):
        row = {"timeframe": "M5", "session": "EUROPE_OPEN", "regime": "TREND_UP",
               "lifecycle": "UNCLASSIFIED", "event_type": "BREAKOUT",
               "recommended_families": "TREND_FOLLOWING", "result_r_proxy": 1}
        a = build_playbooks([row])[0]["playbook_id"]
        b = build_playbooks([row])[0]["playbook_id"]
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("PB_"))
        self.assertEqual(len(a), 19)

    def test_empty_data_does_not_promote(self):
        self.assertEqual(build_playbooks([]), [])


if __name__ == "__main__":
    unittest.main()
