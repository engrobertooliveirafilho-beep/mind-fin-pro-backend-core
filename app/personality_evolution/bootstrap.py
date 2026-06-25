from app.personality_evolution.evolution_engine.engine import PersonalityEvolutionEngine
from app.personality_evolution.feedback_analysis.analyzer import FeedbackAnalyzer
from app.personality_evolution.stability.guard import PersonalityStabilityGuard

class AutonomousPersonalityEngine:
    def __init__(self):
        self.engine = PersonalityEvolutionEngine()
        self.analyzer = FeedbackAnalyzer()
        self.guard = PersonalityStabilityGuard()

    def tick(self, interaction):
        feedback = self.analyzer.analyze(interaction)
        personality = {"adaptive_traits": {}}

        personality = self.engine.evolve(personality, feedback)
        personality = self.guard.enforce(personality)

        return personality
