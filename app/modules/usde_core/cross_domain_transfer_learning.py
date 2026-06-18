from __future__ import annotations

class CrossDomainTransferLearning:
    def transfer(self, source_domain:str, target_domain:str, features:list[str])->dict:
        overlap=len(set(features))

        return {
            "source_domain":source_domain,
            "target_domain":target_domain,
            "shared_features":overlap,
            "transfer_score":min(1.0, overlap/max(1,len(features)))
        }

    def recommend(self, experiments:list[dict])->dict:
        if not experiments:
            return {"recommended":None}

        best=max(
            experiments,
            key=lambda x:x.get("score",0.0)
        )

        return {
            "recommended":best.get("domain"),
            "score":best.get("score",0.0)
        }
