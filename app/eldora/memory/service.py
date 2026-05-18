class EldoramemoryService:
    feature_flag = "ELDORA_CANONICAL_MEMORY"

    def health(self):
        return {
            "family": "memory",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
