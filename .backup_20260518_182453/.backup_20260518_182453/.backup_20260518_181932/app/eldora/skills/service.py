class EldoraskillsService:
    feature_flag = "ELDORA_CANONICAL_SKILLS"

    def health(self):
        return {
            "family": "skills",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
