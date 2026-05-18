class EldoravideoService:
    feature_flag = "ELDORA_CANONICAL_VIDEO"

    def health(self):
        return {
            "family": "video",
            "status": "ready",
            "feature_flag": self.feature_flag,
            "real_revenue_declared": False,
            "lotofacil_promise_of_gain": False
        }
