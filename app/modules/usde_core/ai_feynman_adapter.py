from __future__ import annotations
import math

class AIFeynmanAdapter:
    def dimensional_consistency(self, variables:dict)->dict:
        dims=set(str(v) for v in variables.values())

        return {
            "variables":len(variables),
            "unique_dimensions":len(dims),
            "consistent":len(dims)<=1
        }

    def candidate_equations(self,x:list[float],y:list[float])->list[dict]:
        if not x or not y:
            return []

        candidates=[]

        try:
            ratio=sum(y)/max(sum(x),1e-9)

            candidates.append({
                "equation":f"y={ratio:.6f}*x",
                "family":"linear_scale"
            })
        except Exception:
            pass

        try:
            candidates.append({
                "equation":"y=a*x+b",
                "family":"linear"
            })

            candidates.append({
                "equation":"y=a*x^2+b",
                "family":"quadratic"
            })

            candidates.append({
                "equation":"y=a*exp(b*x)",
                "family":"exponential"
            })
        except Exception:
            pass

        return candidates

    def rank(self,candidates:list[dict])->dict:
        if not candidates:
            return {
                "best_equation":None,
                "count":0
            }

        return {
            "best_equation":candidates[0]["equation"],
            "count":len(candidates)
        }
