class EldoraconsentsService:
    feature_flag = "ELDORA_CANONICAL_CONSENTS"

    def health(self):
        return {
            "family": "consents",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
