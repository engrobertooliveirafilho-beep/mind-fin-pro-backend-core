import unittest
from unittest.mock import patch
from types import SimpleNamespace
from app.runtime import mind_trader_institutional_wiring as wiring

class PaperInputGate(unittest.TestCase):
    def test_invalid_inputs_never_import(self):
        for payload in ("invalid", {"mode": "LIVE"}, {"mode": "DEMO"},
                        {"real_orders": True}, {"ftmo_real": "ENABLED"},
                        {"live_trading": True}):
            with self.subTest(payload=payload), patch.object(wiring.importlib, "import_module") as importer:
                with self.assertRaises(ValueError):
                    wiring.run(payload)
                importer.assert_not_called()

    def test_paper_allowed(self):
        with patch.object(wiring, "MODULES", ["m"]):
            with patch.object(wiring.importlib, "import_module",
                              return_value=SimpleNamespace(run=lambda: {"status": "PASS"})):
                self.assertEqual(wiring.run({"mode": "PAPER_ONLY"})["status"], "operational")

if __name__ == "__main__":
    unittest.main()
