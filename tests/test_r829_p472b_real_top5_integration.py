"""Repository-native read-only integration: bridge AST inventory of the real TOP5 files."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "app/runtime/capability_recovery_bridge.py"
spec = importlib.util.spec_from_file_location("bridge_integration", BRIDGE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class TestRealFiveModules(unittest.TestCase):
    def test_all_real_sources_parse_without_import(self):
        with patch.object(bridge.importlib, "import_module", side_effect=AssertionError("unsafe import")):
            report = bridge.capability_recovery_report(source_root=ROOT, execute_probes=True)
        self.assertEqual(report["summary"]["total"], 5)
        self.assertFalse(report["active_probe_allowed"])
        self.assertEqual(report["summary"]["with_successful_calls"], 0)
        self.assertEqual([m["static_inspection"] for m in report["modules"]], ["parsed_not_executed"] * 5)
    def test_persona_class_declared(self):
        report = bridge.capability_recovery_report(source_root=ROOT)
        persona = next(m for m in report["modules"] if m["module"] == "app.persona.adaptive_social_dialogue")
        self.assertIn("AdaptiveSocialDialogue", persona["classes"])
        self.assertFalse(persona["import_ok"])
    def test_social_api_coroutines_declared(self):
        import ast
        p = ROOT / "app/api/eldora_social.py"
        tree = ast.parse(p.read_text(encoding="utf-8"))
        async_names = [n.name for n in tree.body if isinstance(n, ast.AsyncFunctionDef)]
        self.assertEqual(len(async_names), 6)
        report = bridge.capability_recovery_report(source_root=ROOT)
        api = next(m for m in report["modules"] if m["module"] == "app.api.eldora_social")
        self.assertEqual(sorted(async_names), api["functions"])
    def test_memory_and_retrieval_declarations(self):
        report = bridge.capability_recovery_report(source_root=ROOT)
        entries = {m["module"]: m for m in report["modules"]}
        self.assertIn("store_social_memory", entries["app.eldora.core.persistent_social_memory"]["functions"])
        self.assertIn("RetrievalProvider", entries["app.retrieval.provider"]["classes"])
        self.assertIn("retrieve_cognitive_memory", entries["app.eldora.core.long_term_memory"]["functions"])

if __name__ == "__main__":
    unittest.main()
