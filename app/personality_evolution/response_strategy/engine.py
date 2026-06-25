class ResponseStrategyEngine:
    def select_strategy(self, personality):
        if personality["adaptive_traits"]["directness"] > 0.7:
            return "direct_execution_mode"
        if personality["adaptive_traits"]["empathy"] > 0.7:
            return "collaborative_mode"
        return "balanced_mode"
