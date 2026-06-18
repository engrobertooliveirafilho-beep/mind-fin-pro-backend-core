from __future__ import annotations

class AutoMLEngine:
    def evaluate_candidates(self,candidates:list[dict])->dict:
        if not candidates:
            return {
                "best_model":None,
                "score":0.0
            }

        ranked=sorted(
            candidates,
            key=lambda x:x.get("score",0.0),
            reverse=True
        )

        return {
            "best_model":ranked[0]["name"],
            "score":ranked[0]["score"],
            "candidates":len(ranked)
        }

    def search(self)->dict:
        candidates=[
            {"name":"RandomForest","score":0.61},
            {"name":"XGBoost","score":0.63},
            {"name":"LightGBM","score":0.62},
            {"name":"SVM","score":0.58}
        ]

        return self.evaluate_candidates(candidates)
