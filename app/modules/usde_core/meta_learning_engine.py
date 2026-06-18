from __future__ import annotations

class MetaLearningEngine:
    def rank_experiments(self,experiments:list[dict])->dict:
        if not experiments:
            return {"best":None,"count":0}

        ranked=sorted(
            experiments,
            key=lambda x:x.get("score",0.0),
            reverse=True
        )

        return {
            "best":ranked[0],
            "count":len(ranked)
        }

    def learn(self,history:list[dict])->dict:
        if not history:
            return {
                "recommended_strategy":None,
                "confidence":0.0
            }

        grouped={}

        for h in history:
            k=h["strategy"]
            grouped.setdefault(k,[])
            grouped[k].append(h["score"])

        best=max(
            grouped.items(),
            key=lambda kv: sum(kv[1])/len(kv[1])
        )

        return {
            "recommended_strategy":best[0],
            "confidence":sum(best[1])/len(best[1])
        }
