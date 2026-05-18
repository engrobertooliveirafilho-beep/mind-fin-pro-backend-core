class EldoralotofacilService:
    feature_flag = "ELDORA_CANONICAL_LOTOFACIL"

    def health(self):
        return {
            "family": "lotofacil",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
