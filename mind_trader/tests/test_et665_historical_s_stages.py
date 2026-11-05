"""ET665: non-executing, fail-closed historical integrity and regression checks."""
import ast
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "mind_trader/historical/s_stages"
HASHES = {
    "S11/controlled_runtime_materialization_probe.py": "052cc81ca7b85f92337609fac72b1ac0ac0b12bb59b7e2251b5d5ed51a054da6",
    "S15/supervised_continuous_paper_runtime.py": "1a52b99d2a257e6d0a179624188bfd34e068484f130a32d807dbf263b9f4f999",
    "S16/extended_supervised_paper_market_replay.py": "643f9a993565130281b8881b206176abc9196124fcd65a92f73595d6f091722b",
    "S17/simulator_activation_candidate_feed.py": "f4bd3a2f0f517873d58cbb59befee0428b03e19efb53727db86d6e22ea8d5d01",
    "S18/ftmo_rule_shadow_failure_injection.py": "72c25c2b77410e328354c8261a3a993c1f683da7cb7fd0e19e0023f6685e7430",
    "S19/multi_day_equity_replay.py": "3855783e2504a90c764eae75c2a50919879fbeb5085d2af73cae776001bbeebf",
}

class HistoricalArchiveTests(unittest.TestCase):
    def test_original_hashes_and_syntax(self):
        for name, expected in HASHES.items():
            with self.subTest(name=name):
                content = (SOURCES / name).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), expected)
                ast.parse(content, filename=name)

    def test_s18_historical_failure_remains_fail_closed(self):
        evidence = json.loads((SOURCES / "evidence/S18_FTMO_RULE_SHADOW_RESULT.json").read_text())
        self.assertEqual(evidence["status"], "CONTROLLED_FTMO_RULE_SHADOW_FAIL")
        self.assertEqual(evidence["failure_injection"]["fail"], 1)
        self.assertEqual(evidence["failure_injection"]["total"], 16)
        self.assertIs(evidence["checks"]["failure_fail_zero"], False)
        self.assertIs(evidence["safety"]["order_execution"], False)

    def test_s19_historical_failure_remains_fail_closed(self):
        evidence = json.loads((SOURCES / "evidence/S19_MULTI_DAY_EQUITY_RESULT.json").read_text())
        self.assertEqual(evidence["status"], "EXTENDED_FTMO_SHADOW_AND_MULTI_DAY_REPLAY_FAIL")
        self.assertEqual(evidence["summary"]["failure_injections"], 0)
        self.assertIs(evidence["checks"]["failure_injections_positive"], False)
        self.assertEqual(evidence["summary"]["order_api_invocations"], 0)

    def test_s19_injection_schedule_is_unreachable_on_trading_days(self):
        injection_days = [d for d in range(1, 61) if d % 7 == 0]
        self.assertEqual(injection_days, [7, 14, 21, 28, 35, 42, 49, 56])
        self.assertTrue(all((d - 1) % 7 in (5, 6) for d in injection_days))
        code = (SOURCES / "S19/multi_day_equity_replay.py").read_text()
        self.assertIn("FAILURE_INJECTION_EVERY_DAYS = 7", code)
        self.assertIn("weekday = (simulated_day - 1) % 7", code)
        self.assertIn("simulated_day % FAILURE_INJECTION_EVERY_DAYS == 0", code)

    def test_s18_failure_gate_is_not_overridden(self):
        code = (SOURCES / "S18/ftmo_rule_shadow_failure_injection.py").read_text()
        self.assertIn("'failure_fail_zero':failure_fail==0", code)
        self.assertIn("ok=all(checks.values())", code)

if __name__ == "__main__":
    unittest.main()
