class PersonalityEvolutionEngine:
    def evolve(self, personality, feedback):
        # feedback-driven trait adjustment
        if feedback.get("confusion"):
            personality["adaptive_traits"]["directness"] += 0.1

        if feedback.get("user_prefers_depth"):
            personality["adaptive_traits"]["analytical_depth"] += 0.1

        return personality
