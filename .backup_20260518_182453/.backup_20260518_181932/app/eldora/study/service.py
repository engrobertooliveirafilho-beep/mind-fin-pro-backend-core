class EldorastudyService:
    feature_flag = "ELDORA_CANONICAL_STUDY"

    def health(self):
        return {
            "family": "study",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
