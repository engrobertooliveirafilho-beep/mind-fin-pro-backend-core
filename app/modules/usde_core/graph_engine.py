from __future__ import annotations
from collections import defaultdict

class GraphEngine:
    def cooccurrence_graph(self, events:list[dict])->dict:
        graph=defaultdict(lambda: defaultdict(int))

        for e in events:
            vals=sorted(set(e["values"]))

            for i,a in enumerate(vals):
                for b in vals[i+1:]:
                    graph[a][b]+=1
                    graph[b][a]+=1

        return {
            str(k): {str(n): w for n,w in v.items()}
            for k,v in graph.items()
        }

    def degree_centrality(self, graph:dict)->dict:
        return {
            node: len(neighbors)
            for node,neighbors in graph.items()
        }

    def weighted_degree(self, graph:dict)->dict:
        return {
            node: sum(neighbors.values())
            for node,neighbors in graph.items()
        }
