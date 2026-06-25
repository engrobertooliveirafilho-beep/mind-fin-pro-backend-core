class IntentReconstructionEngine:
    def reconstruct(self, user_input):
        return {
            "intent": "inferred",
            "confidence": 0.72,
            "missing_fields": self.detect_gaps(user_input)
        }

    def detect_gaps(self, text):
        gaps = []
        if "?" not in text:
            gaps.append("missing_clarity")
        return gaps
