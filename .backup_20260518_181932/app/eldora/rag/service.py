class EldoraragService:
    feature_flag = "ELDORA_CANONICAL_RAG"

    def health(self):
        return {
            "family": "rag",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
