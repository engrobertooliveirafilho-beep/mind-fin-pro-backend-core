class EldoraidentityService:
    feature_flag = "ELDORA_CANONICAL_IDENTITY"

    def health(self):
        return {
            "family": "identity",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
