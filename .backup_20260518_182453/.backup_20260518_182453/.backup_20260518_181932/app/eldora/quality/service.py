class EldoraqualityService:
    feature_flag = "ELDORA_CANONICAL_QUALITY"

    def health(self):
        return {
            "family": "quality",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
