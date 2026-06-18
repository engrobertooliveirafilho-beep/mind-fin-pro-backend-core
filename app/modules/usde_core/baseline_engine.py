from __future__ import annotations
import random, statistics

class BaselineEngine:
    def uniform_baseline(self, universe_size:int, sample_size:int)->dict:
        return {
            "name":"uniform",
            "universe_size":universe_size,
            "sample_size":sample_size,
            "expected_hit_rate": sample_size/max(universe_size,1)
        }

    def random_baseline(self, universe:list[int], sample_size:int, trials:int=1000)->dict:
        scores=[]
        for _ in range(trials):
            scores.append(len(set(random.sample(universe,min(sample_size,len(universe))))))
        return {
            "name":"random",
            "trials":trials,
            "mean":statistics.mean(scores),
            "stdev":statistics.pstdev(scores)
        }

    def persistence_baseline(self, last_event:list[int])->dict:
        return {
            "name":"persistence",
            "prediction":sorted(set(last_event))
        }

    def frequency_baseline(self, freq_metrics:dict, top_k:int)->dict:
        ranked=sorted(freq_metrics,key=lambda x:freq_metrics[x]["frequency"],reverse=True)
        return {
            "name":"frequency",
            "prediction":[int(x) for x in ranked[:top_k]]
        }

    def bayesian_baseline(self, freq_metrics:dict)->dict:
        probs={k:v["frequency"] for k,v in freq_metrics.items()}
        return {
            "name":"bayesian",
            "posterior":probs
        }
