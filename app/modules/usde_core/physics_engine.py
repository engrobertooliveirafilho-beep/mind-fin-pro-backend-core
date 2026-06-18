from __future__ import annotations
import math

class PhysicsEngine:
    def random_walk_metrics(self, series:list[float])->dict:
        if len(series)<2:
            return {"steps":0,"drift":0.0,"volatility":0.0}

        diffs=[
            series[i]-series[i-1]
            for i in range(1,len(series))
        ]

        drift=sum(diffs)/len(diffs)

        variance=sum(
            (x-drift)**2
            for x in diffs
        )/len(diffs)

        return {
            "steps":len(diffs),
            "drift":drift,
            "volatility":math.sqrt(variance)
        }

    def poisson_process_score(self, counts:list[int])->dict:
        if not counts:
            return {"lambda":0.0,"variance":0.0}

        lam=sum(counts)/len(counts)

        variance=sum(
            (x-lam)**2
            for x in counts
        )/len(counts)

        return {
            "lambda":lam,
            "variance":variance,
            "dispersion_index":(
                variance/lam
                if lam>0
                else 0.0
            )
        }

    def criticality_proxy(self, series:list[float])->dict:
        if len(series)<3:
            return {"criticality":0.0}

        diffs=[
            abs(series[i]-series[i-1])
            for i in range(1,len(series))
        ]

        spikes=sum(
            1
            for d in diffs
            if d > (sum(diffs)/len(diffs))
        )

        return {
            "criticality":spikes/max(1,len(diffs))
        }
