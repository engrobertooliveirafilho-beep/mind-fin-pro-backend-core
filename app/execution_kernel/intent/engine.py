class IntentEngine:
    def parse(self, user_input):
        return {
            "intent": user_input,
            "status": "ACTIVE",
            "confidence": 0.9
        }
