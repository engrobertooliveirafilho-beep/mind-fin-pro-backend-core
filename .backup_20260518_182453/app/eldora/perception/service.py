class EldoraperceptionService:
    feature_flag = "ELDORA_CANONICAL_PERCEPTION"

    def health(self):
        return {
            "family": "perception",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
