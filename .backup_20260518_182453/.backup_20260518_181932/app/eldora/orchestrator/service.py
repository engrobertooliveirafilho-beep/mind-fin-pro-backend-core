class EldoraorchestratorService:
    feature_flag = "ELDORA_CANONICAL_ORCHESTRATOR"

    def health(self):
        return {
            "family": "orchestrator",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
