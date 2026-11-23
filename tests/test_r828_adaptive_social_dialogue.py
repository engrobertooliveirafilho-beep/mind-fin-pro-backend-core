import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "app/persona/adaptive_social_dialogue.py"
spec = importlib.util.spec_from_file_location("persona_under_test", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestAdaptiveSocialDialogue(unittest.TestCase):
    def setUp(self):
        self.persona = module.AdaptiveSocialDialogue()
    def test_marketing(self):
        self.assertIn("ativo de retenção", self.persona.adapt("Resposta.", "marketing digital"))
    def test_branding(self):
        self.assertIn("ativo de retenção", self.persona.adapt("Resposta.", "branding"))
    def test_product(self):
        self.assertIn("consistência", self.persona.adapt("Resposta.", "produto"))
    def test_brand(self):
        self.assertIn("consistência", self.persona.adapt("Resposta.", "marca"))
    def test_neura(self):
        self.assertIn("consistência", self.persona.adapt("Resposta.", "neura"))
    def test_unrelated(self):
        self.assertEqual("Resposta.", self.persona.adapt("Resposta.", "clima"))
    def test_none_message(self):
        self.assertEqual("Resposta.", self.persona.adapt("Resposta.", None))
    def test_precedence(self):
        self.assertIn("consistência", self.persona.adapt("Resposta.", "produto marketing"))

if __name__ == "__main__":
    unittest.main()
