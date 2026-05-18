class EldorareasoningService:
    feature_flag = "ELDORA_CANONICAL_REASONING"

    def health(self):
        return {
            "family": "reasoning",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
