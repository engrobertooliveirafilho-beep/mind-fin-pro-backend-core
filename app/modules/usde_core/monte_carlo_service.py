from __future__ import annotations
from app.modules.usde_core.monte_carlo_engine import MonteCarloEngine

class MonteCarloService:
    def run(self,universe:list[int],sample_size:int,trials:int=1000):
        result=MonteCarloEngine().simulate(
            universe,
            sample_size,
            trials
        )

        return {
            "status":"COMPLETED",
            "trials":result["trials"],
            "mean":result["mean"],
            "stdev":result["stdev"]
        }
