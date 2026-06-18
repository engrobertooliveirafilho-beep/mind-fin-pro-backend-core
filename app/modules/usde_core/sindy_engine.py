from __future__ import annotations

class SINDyEngine:
    def finite_difference(self,x:list[float])->list[float]:
        if len(x)<2:
            return []
        return [
            x[i]-x[i-1]
            for i in range(1,len(x))
        ]

    def discover_dynamics(self,series:list[float])->dict:
        dx=self.finite_difference(series)

        if not dx:
            return {
                "equation":"dx/dt = 0",
                "coefficients":[0.0]
            }

        mean_dx=sum(dx)/len(dx)
        mean_x=sum(series[:-1])/max(1,len(series[:-1]))

        coeff=(
            mean_dx/mean_x
            if mean_x!=0
            else 0.0
        )

        return {
            "equation":f"dx/dt = {coeff:.6f} * x",
            "coefficients":[coeff],
            "samples":len(series)
        }
