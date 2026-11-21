import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.runtime import mind_trader_institutional_wiring as wiring


class InstitutionalWiringSafetyTests(unittest.TestCase):
    def _project(self, source):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        runtime = root / "app" / "runtime"
        runtime.mkdir(parents=True)
        (runtime / "wiring.py").write_text("# fixture", encoding="utf-8")
        (runtime / "paper_motor.py").write_text(source, encoding="utf-8")
        self.addCleanup(tmp.cleanup)
        return root / "app" / "runtime" / "wiring.py"

    def test_discovery_is_static_and_never_imports_or_executes(self):
        fake_file = self._project(
            "CALLS = []\ndef run(payload):\n    CALLS.append(payload)\n"
            "def health():\n    CALLS.append('health')\nclass Motor: pass\n"
        )
        with patch.object(wiring, "__file__", str(fake_file)), patch.object(wiring, "MODULES", ["app.runtime.paper_motor"]):
            result = wiring.run_institutional_wiring({"intent": "PAPER"})
        self.assertEqual(result["status"], "SOURCE_INSPECTION_OK_UNCERTIFIED")
        self.assertEqual(result["source_inspections_ok"], 1)
        self.assertEqual(result["imports_ok"], 0)
        self.assertFalse(result["execution_performed"])
        self.assertEqual(result["results"][0]["functions"], ["run", "health"])
        self.assertEqual(result["results"][0]["classes"], ["Motor"])
        self.assertFalse(result["results"][0]["import_performed"])
        self.assertFalse(hasattr(wiring, "importlib"))

    def test_missing_source_degrades(self):
        fake_file = self._project("# no motor file")
        with patch.object(wiring, "__file__", str(fake_file)), patch.object(wiring, "MODULES", ["app.runtime.absent"]):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["results"][0]["error"], "SOURCE_NOT_FOUND")

    def test_invalid_python_source_degrades(self):
        fake_file = self._project("def broken(:\n pass\n")
        with patch.object(wiring, "__file__", str(fake_file)), patch.object(wiring, "MODULES", ["app.runtime.paper_motor"]):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertTrue(result["results"][0]["error"].startswith("SOURCE_INVALID:"))

    def test_invalid_payload_rejected(self):
        for invalid in ("unsafe", "", 0, False, []):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "INVALID_PAYLOAD"):
                    wiring.run_institutional_wiring(invalid)

    def test_health_is_static_and_uncertified(self):
        fake_file = self._project("def run(): pass\n")
        with patch.object(wiring, "__file__", str(fake_file)), patch.object(wiring, "MODULES", ["app.runtime.paper_motor"]):
            result = wiring.health()
        self.assertEqual(result["status"], "SOURCE_INSPECTION_OK_UNCERTIFIED")
        self.assertEqual(result["runs_ok"], 0)
        self.assertFalse(result["execution_performed"])


if __name__ == "__main__":
    unittest.main()
