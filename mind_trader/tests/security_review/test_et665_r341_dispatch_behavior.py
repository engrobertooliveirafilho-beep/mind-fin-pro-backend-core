"""ET665.R341 — behavioral dispatch isolation tests, synthetic modules only.

These tests do not certify historical HP19 membership or real agents.
"""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / "experimental/et665_r340_safe_agent_dispatch.py"

def load_dispatch():
    spec = importlib.util.spec_from_file_location("et665_r341_dispatch", SOURCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class SafeDispatchBehavior(unittest.TestCase):
    def test_all_candidates_route_to_distinct_concrete_runners(self):
        dispatch = load_dispatch()
        calls = []
        fake_modules = {}
        for name in dispatch.AGENT_MODULES:
            module = types.ModuleType("app.agents." + name)
            def run_dry(payload, agent=name):
                calls.append((agent, payload))
                return {"agent_id": agent, "processed": payload["component"], "status": "processed"}
            module.run_dry = run_dry
            fake_modules["app.agents." + name] = module
        with patch.dict(sys.modules, fake_modules):
            for name in dispatch.AGENT_MODULES:
                result = dispatch.run_agent(name, {"component": "synthetic_test"})
                self.assertEqual(result["agent_id"], name)
                self.assertEqual(result["processed"], "synthetic_test")
        self.assertEqual(len(calls), len(dispatch.AGENT_MODULES))
        self.assertEqual([name for name, _ in calls], list(dispatch.AGENT_MODULES))
        self.assertEqual(len(set(name for name, _ in calls)), len(calls))

    def test_unknown_agent_rejected(self):
        dispatch = load_dispatch()
        with self.assertRaises(ValueError):
            dispatch.run_agent("../outside", {"component": "synthetic_test"})

    def test_missing_module_fails_closed(self):
        dispatch = load_dispatch()
        with patch.object(dispatch, "import_module", side_effect=ModuleNotFoundError("missing")):
            with self.assertRaises(ModuleNotFoundError):
                dispatch.run_agent(dispatch.AGENT_MODULES[0], {"component": "synthetic_test"})

    def test_error_and_stub_results_rejected(self):
        dispatch = load_dispatch()
        for result in ({"error": "failed"}, {"status": "stub"}, {"not_implemented": True}, {}, None):
            with self.subTest(result=result):
                fake = types.SimpleNamespace(run_dry=lambda payload: result)
                with patch.object(dispatch, "import_module", return_value=fake):
                    with self.assertRaises(RuntimeError):
                        dispatch.run_agent(dispatch.AGENT_MODULES[0], {"component": "synthetic_test"})

if __name__ == "__main__":
    unittest.main()
