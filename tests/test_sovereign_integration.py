import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.runtime import sovereign_conversation_orchestrator as motor

class SovereignIntegration(unittest.TestCase):
    def test_profile_transition_and_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(motor, "_STATE_FILE", Path(tmp)/"state.json"), patch.object(motor, "_trace_state"):
                motor.decide("a", "monte minha dieta")
                result = motor.decide("a", "80 kg, 1,75, 30 anos, treino manhã, 4 refeições, ganhar massa")
                self.assertEqual(result.goal, "perfil alimentar coletado")
                self.assertIn("ganhar massa", result.answer)
                self.assertIn("4", result.answer)
                motor.decide("b", "olá")
                state = motor._load_all_state()
                self.assertEqual(state["a"]["goal"], result.goal)
                self.assertFalse(state["b"]["fitness_slots"])

    def test_universal_routing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(motor, "_STATE_FILE", Path(tmp)/"state.json"), patch.object(motor, "_trace_state"):
                self.assertEqual(motor.decide("a", "backtest").domain, "trader")
                self.assertEqual(motor.decide("b", "github").domain, "tech")

if __name__ == "__main__":
    unittest.main()
