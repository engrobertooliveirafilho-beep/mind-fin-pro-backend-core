class EldorabillingService:
    feature_flag = "ELDORA_CANONICAL_BILLING"

    def health(self):
        return {
            "family": "billing",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
