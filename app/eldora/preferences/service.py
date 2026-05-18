class EldorapreferencesService:
    feature_flag = "ELDORA_CANONICAL_PREFERENCES"

    def health(self):
        return {
            "family": "preferences",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
