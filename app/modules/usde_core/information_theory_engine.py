from __future__ import annotations
import math

class InformationTheoryEngine:
    def entropy(self, probs:list[float])->float:
        return -sum(
            p * math.log2(p)
            for p in probs
            if p > 0
        )

    def frequency_entropy(self, events:list[dict])->dict:
        counts={}
        total=0

        for e in events:
            for v in e["values"]:
                counts[v]=counts.get(v,0)+1
                total+=1

        probs=[c/total for c in counts.values()]

        return {
            "entropy": self.entropy(probs),
            "symbols": len(counts)
        }

    def mutual_information_binary(self,x:list[int],y:list[int])->float:
        n=min(len(x),len(y))
        if n==0:
            return 0.0

        joint={}
        px={}
        py={}

        for a,b in zip(x[:n],y[:n]):
            joint[(a,b)] = joint.get((a,b),0)+1
            px[a]=px.get(a,0)+1
            py[b]=py.get(b,0)+1

        mi=0.0

        for (a,b),c in joint.items():
            pab=c/n
            pa=px[a]/n
            pb=py[b]/n
            mi += pab * math.log2(pab/(pa*pb))

        return mi
