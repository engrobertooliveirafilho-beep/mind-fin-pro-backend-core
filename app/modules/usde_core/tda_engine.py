from __future__ import annotations

class TDAEngine:
    def persistence_score(self, events:list[dict])->dict:
        counts={}

        for e in events:
            for v in e["values"]:
                counts[v]=counts.get(v,0)+1

        if not counts:
            return {
                "features":0,
                "max_persistence":0.0,
                "avg_persistence":0.0
            }

        vals=list(counts.values())

        return {
            "features":len(vals),
            "max_persistence":max(vals),
            "avg_persistence":sum(vals)/len(vals)
        }

    def betti_proxy(self, events:list[dict])->dict:
        nodes=set()
        edges=set()

        for e in events:
            vals=sorted(set(e["values"]))

            for v in vals:
                nodes.add(v)

            for i,a in enumerate(vals):
                for b in vals[i+1:]:
                    edges.add((a,b))

        return {
            "betti_0_proxy":len(nodes),
            "betti_1_proxy":max(0,len(edges)-len(nodes)+1)
        }
