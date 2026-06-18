from __future__ import annotations
import math

class SymbolicRegressionEngine:
    def fit_linear(self,x:list[float],y:list[float])->dict:
        n=min(len(x),len(y))

        if n<2:
            return {
                "equation":"y=0",
                "r2":0.0
            }

        mx=sum(x[:n])/n
        my=sum(y[:n])/n

        num=sum(
            (x[i]-mx)*(y[i]-my)
            for i in range(n)
        )

        den=sum(
            (x[i]-mx)**2
            for i in range(n)
        )

        a=num/den if den else 0.0
        b=my-a*mx

        yhat=[a*v+b for v in x[:n]]

        ssr=sum(
            (y[i]-yhat[i])**2
            for i in range(n)
        )

        sst=sum(
            (y[i]-my)**2
            for i in range(n)
        )

        r2=1-(ssr/sst) if sst else 0.0

        return {
            "equation":f"y={a:.6f}x+{b:.6f}",
            "a":a,
            "b":b,
            "r2":r2
        }

    def discover(self,x:list[float],y:list[float])->dict:
        linear=self.fit_linear(x,y)

        return {
            "best_model":"linear",
            "equation":linear["equation"],
            "r2":linear["r2"]
        }
