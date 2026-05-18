class EldorallmService:
    feature_flag = "ELDORA_CANONICAL_LLM"

    def health(self):
        return {
            "family": "llm",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
