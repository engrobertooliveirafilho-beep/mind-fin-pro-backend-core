class EldoraplansService:
    feature_flag = "ELDORA_CANONICAL_PLANS"

    def health(self):
        return {
            "family": "plans",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
