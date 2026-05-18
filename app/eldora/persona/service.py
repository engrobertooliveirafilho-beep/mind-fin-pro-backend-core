class EldorapersonaService:
    feature_flag = "ELDORA_CANONICAL_PERSONA"

    def health(self):
        return {
            "family": "persona",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
