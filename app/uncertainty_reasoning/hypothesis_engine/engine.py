class HypothesisEngine:
    def generate(self, input_text):
        return [
            {"intent": "informational", "confidence": 0.6},
            {"intent": "action_request", "confidence": 0.3},
            {"intent": "emotional_support", "confidence": 0.1}
        ]
