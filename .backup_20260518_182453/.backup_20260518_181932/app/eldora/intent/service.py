class EldoraintentService:
    feature_flag = "ELDORA_CANONICAL_INTENT"

    def health(self):
        return {
            "family": "intent",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
