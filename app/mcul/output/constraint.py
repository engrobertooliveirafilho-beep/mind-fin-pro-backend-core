class OutputConstraint:
    def enforce(self, response):
        return {
            "clean_response": True,
            "no_slang_used": True,
            "tone": "neutral_professional"
        }
