from __future__ import annotations

class EnsembleEvolutionEngine:
    def weighted_vote(self,models:list[dict])->dict:
        if not models:
            return {"score":0.0,"models":0}

        total_weight=sum(
            m.get("weight",1.0)
            for m in models
        )

        score=sum(
            m.get("score",0.0)*m.get("weight",1.0)
            for m in models
        )/max(total_weight,1e-9)

        return {
            "ensemble_score":score,
            "models":len(models)
        }

    def evolve(self,generations:list[list[dict]])->dict:
        history=[]

        for generation in generations:
            history.append(
                self.weighted_vote(generation)["ensemble_score"]
            )

        best=max(history) if history else 0.0

        return {
            "best_score":best,
            "generations":len(history),
            "improvement":(
                best-history[0]
                if history
                else 0.0
            )
        }
