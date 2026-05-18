class EldorasecurityService:
    feature_flag = "ELDORA_CANONICAL_SECURITY"

    def health(self):
        return {
            "family": "security",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
