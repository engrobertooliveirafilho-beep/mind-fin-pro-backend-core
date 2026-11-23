"""Offline regression: patch imports; never start a broker or live runtime."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "app/runtime/mind_trader_institutional_wiring.py"

class WiringIsolationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("isolated_trader_wiring", SOURCE)
        cls.wiring = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.wiring)

    def test_health_is_pure(self):
        with patch.object(self.wiring.importlib, "import_module", side_effect=AssertionError("import attempted")):
            result = self.wiring.health()
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertTrue(result["inspection_only"])

    def test_unsafe_payload_rejected_before_import(self):
        cases = [("mode", "LIVE"), ("execution_mode", "LIVE"), ("account_mode", "REAL"),
                 ("real_orders", True), ("real_orders", 0), ("ftmo_real", True), ("ftmo_real", 0), ("real_orders_allowed", True),
                 ("live", True), ("live_trading", True), ("broker_execution", True)]
        for key, value in cases:
            with self.subTest(key=key):
                with patch.object(self.wiring.importlib, "import_module", side_effect=AssertionError("import attempted")):
                    with self.assertRaises(ValueError):
                        self.wiring.run_institutional_wiring({"mode": "PAPER_ONLY", key: value})

    def test_failed_or_ambiguous_motor_results(self):
        for result in ({}, {"status": "PENDING"}, {"ok": True, "status": "UNVERIFIED"}, {"status": "PASS", "error": "failed"},
                       {"ok": False}, False, None):
            with self.subTest(result=result):
                motor = SimpleNamespace(run=lambda payload: result)
                with patch.object(self.wiring, "MODULES", ["fake.motor"]), patch.object(self.wiring.importlib, "import_module", return_value=motor):
                    output = self.wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
                self.assertEqual(output["status"], "DEGRADED")
                self.assertEqual(output["runs_ok"], 0)

    def test_explicit_paper_success_is_not_certification(self):
        motor = SimpleNamespace(run=lambda payload: {"status": "PASS"})
        with patch.object(self.wiring, "MODULES", ["fake.motor"]), patch.object(self.wiring.importlib, "import_module", return_value=motor):
            output = self.wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
        self.assertEqual(output["status"], "PAPER_RUN_COMPLETED_UNCERTIFIED")
        self.assertEqual(output["runs_ok"], 1)

    def test_legacy_simulation_adapters_bounded(self):
        engines = [
            ("app.runtime.p2223_broker_emulator", "run_simulation", "BROKER_EMULATOR_SIMULATION_ONLY"),
            ("app.runtime.p2224_2226_institutional_core", "run", "INSTITUTIONAL_SIMULATION_CORE"),
            ("app.runtime.p2227_2229_advanced_layer", "run", "ADVANCED_SIMULATION_LAYER"),
        ]
        for name, fn_name, mode in engines:
            with self.subTest(name=name):
                calls = []
                def simulation(*, cycles):
                    calls.append(cycles)
                    return {"status": "PASS", "mode": mode}
                motor = SimpleNamespace(**{fn_name: simulation})
                with patch.object(self.wiring, "MODULES", [name]), patch.object(self.wiring.importlib, "import_module", return_value=motor):
                    output = self.wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
                self.assertEqual(calls, [1])
                self.assertEqual(output["runs_ok"], 1)
                self.assertEqual(output["status"], "PAPER_RUN_COMPLETED_UNCERTIFIED")

    def test_legacy_adapter_rejects_contradictory_failure(self):
        motor = SimpleNamespace(run=lambda *, cycles: {"status": "PASS", "mode": "INSTITUTIONAL_SIMULATION_CORE", "ok": False})
        with patch.object(self.wiring, "MODULES", ["app.runtime.p2224_2226_institutional_core"]), patch.object(self.wiring.importlib, "import_module", return_value=motor):
            output = self.wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
        self.assertEqual(output["status"], "DEGRADED")
        self.assertEqual(output["runs_ok"], 0)

    def test_legacy_adapter_rejects_wrong_mode(self):
        motor = SimpleNamespace(run=lambda *, cycles: {"status": "PASS", "mode": "LIVE"})
        with patch.object(self.wiring, "MODULES", ["app.runtime.p2224_2226_institutional_core"]), patch.object(self.wiring.importlib, "import_module", return_value=motor):
            output = self.wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
        self.assertEqual(output["status"], "DEGRADED")
        self.assertEqual(output["runs_ok"], 0)
