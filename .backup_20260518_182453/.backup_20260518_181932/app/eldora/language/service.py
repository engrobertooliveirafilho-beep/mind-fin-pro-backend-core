class EldoralanguageService:
    feature_flag = "ELDORA_CANONICAL_LANGUAGE"

    def health(self):
        return {
            "family": "language",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
