from __future__ import annotations
from app.modules.usde_core.walk_forward_engine import WalkForwardEngine

class WalkForwardService:
    def run(self,events:list[dict]):
        def predictor(train):
            return train[-1]["values"]

        result=WalkForwardEngine().evaluate(
            events,
            predictor
        )

        return {
            "status":"COMPLETED",
            "evaluations":result["evaluations"],
            "avg_accuracy":result["avg_accuracy"]
        }
