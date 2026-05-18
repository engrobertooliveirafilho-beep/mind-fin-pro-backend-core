class EldoraknowledgeService:
    feature_flag = "ELDORA_CANONICAL_KNOWLEDGE"

    def health(self):
        return {
            "family": "knowledge",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
