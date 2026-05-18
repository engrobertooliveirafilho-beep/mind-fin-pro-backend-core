class EldoramediaService:
    feature_flag = "ELDORA_CANONICAL_MEDIA"

    def health(self):
        return {
            "family": "media",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
