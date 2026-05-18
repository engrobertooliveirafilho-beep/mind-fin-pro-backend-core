class EldoralgpdService:
    feature_flag = "ELDORA_CANONICAL_LGPD"

    def health(self):
        return {
            "family": "lgpd",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
