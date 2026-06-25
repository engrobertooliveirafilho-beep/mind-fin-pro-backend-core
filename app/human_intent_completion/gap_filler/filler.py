class SemanticGapFiller:
    def fill(self, intent):
        if "missing_clarity" in intent.get("missing_fields", []):
            intent["clarification_needed"] = True
        return intent
