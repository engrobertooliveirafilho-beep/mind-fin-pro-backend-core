"""HP19 deny-all quarantine regression; offline and without agent imports."""
import json
import unittest
from pathlib import Path
from app.meta.agents_unified_runtime import AgentDispatchError, REG_PATH, run_agent


class TestHP19Quarantine(unittest.TestCase):
    def test_registry_is_deny_all(self):
        data = json.loads(REG_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["activation_policy"], "DENY_ALL_UNTIL_INDIVIDUAL_EVIDENCE")
        self.assertEqual(data["agents"], [])

    def test_historical_agent_cannot_execute(self):
        with self.assertRaises(AgentDispatchError):
            run_agent("cog.autonomous_maturity_meter", {"probe": True})

    def test_unknown_agent_cannot_execute(self):
        with self.assertRaises(AgentDispatchError):
            run_agent("unknown.agent", {"probe": True})

    def test_invalid_request_cannot_execute(self):
        with self.assertRaises(AgentDispatchError):
            run_agent("", {"probe": True})


if __name__ == "__main__":
    unittest.main()
