from app.self_evolution.evolution_controller import EvolutionController
from app.cognitive_os.graph_core import CognitiveGraphEngine
from app.observability.system_drift_detector import DriftDetector

class SelfEvolvingCognitiveOS:
    def __init__(self):
        self.graph = CognitiveGraphEngine()
        self.evolver = EvolutionController()
        self.drift = DriftDetector()

    def tick(self, system_state):
        drift = self.drift.analyze(system_state)

        if drift["severity"] > 0.7:
            return self.evolver.mutate(self.graph, drift)

        return "STABLE"
