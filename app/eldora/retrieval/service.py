class EldoraretrievalService:
    feature_flag = "ELDORA_CANONICAL_RETRIEVAL"

    def health(self):
        return {
            "family": "retrieval",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
