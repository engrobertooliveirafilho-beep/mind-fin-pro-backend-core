class UserIntentTranslator:
    def translate(self, raw_input):
        return {
            "structured_intent": True,
            "raw": raw_input,
            "interpreted_goal": "inferred_goal"
        }
