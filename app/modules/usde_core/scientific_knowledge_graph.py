from __future__ import annotations

class ScientificKnowledgeGraph:
    def __init__(self):
        self.nodes={}
        self.edges=[]

    def add_node(self,node_id:str,node_type:str,metadata:dict|None=None):
        self.nodes[node_id]={
            "type":node_type,
            "metadata":metadata or {}
        }

    def add_edge(self,source:str,target:str,relation:str):
        self.edges.append({
            "source":source,
            "target":target,
            "relation":relation
        })

    def summary(self)->dict:
        return {
            "nodes":len(self.nodes),
            "edges":len(self.edges)
        }

    def neighbors(self,node_id:str)->list[str]:
        result=[]

        for e in self.edges:
            if e["source"]==node_id:
                result.append(e["target"])

        return result
