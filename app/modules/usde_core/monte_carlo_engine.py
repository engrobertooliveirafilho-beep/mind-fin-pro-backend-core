from __future__ import annotations
import random, statistics, math

class MonteCarloEngine:
    def simulate(self, universe:list[int], sample_size:int, trials:int=10000)->dict:
        scores=[]
        for _ in range(trials):
            draw=set(random.sample(universe,min(sample_size,len(universe))))
            scores.append(len(draw))

        return {
            "trials":trials,
            "mean":statistics.mean(scores),
            "stdev":statistics.pstdev(scores),
            "min":min(scores),
            "max":max(scores)
        }

    def compare(self, model_score:float, baseline_score:float, trials:int=10000)->dict:
        delta=model_score-baseline_score
        z=delta/max(0.0001,abs(baseline_score))
        return {
            "model_score":model_score,
            "baseline_score":baseline_score,
            "delta":delta,
            "effect_size":z,
            "better_than_baseline":delta>0
        }
