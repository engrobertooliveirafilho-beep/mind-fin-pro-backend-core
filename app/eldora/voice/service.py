class EldoravoiceService:
    feature_flag = "ELDORA_CANONICAL_VOICE"

    def health(self):
        return {
            "family": "voice",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
