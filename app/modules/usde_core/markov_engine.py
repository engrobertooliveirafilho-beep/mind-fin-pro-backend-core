from __future__ import annotations
from collections import Counter

class MarkovEngine:
    def transition_matrix(self, events:list[dict])->dict:
        states=sorted(set(v for e in events for v in e["values"]))
        transitions={s:Counter() for s in states}
        totals=Counter()

        for a,b in zip(events,events[1:]):
            A=set(a["values"])
            B=set(b["values"])

            for x in A:
                totals[x]+=1
                for y in B:
                    transitions[x][y]+=1

        matrix={}
        for x in states:
            matrix[str(x)]={}
            for y in states:
                matrix[str(x)][str(y)]=(
                    transitions[x][y]/totals[x]
                    if totals[x]
                    else 0.0
                )

        return matrix

    def persistence_score(self, events:list[dict])->dict:
        score={}

        for a,b in zip(events,events[1:]):
            for n in a["values"]:
                score.setdefault(n,[0,0])
                score[n][0]+=1
                if n in b["values"]:
                    score[n][1]+=1

        return {
            str(k):(v[1]/v[0] if v[0] else 0)
            for k,v in score.items()
        }
