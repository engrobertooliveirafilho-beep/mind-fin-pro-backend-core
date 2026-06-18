from __future__ import annotations
from app.modules.usde_core.scientific_knowledge_graph import ScientificKnowledgeGraph

class ScientificKnowledgeSync:
    def sync(self,hypothesis_id:str,experiment_id:str,evidence_id:str,decision_id:str):
        graph=ScientificKnowledgeGraph()

        graph.add_node(hypothesis_id,"hypothesis")
        graph.add_node(experiment_id,"experiment")
        graph.add_node(evidence_id,"evidence")
        graph.add_node(decision_id,"decision")

        graph.add_edge(hypothesis_id,experiment_id,"tested_by")
        graph.add_edge(experiment_id,evidence_id,"generated")
        graph.add_edge(evidence_id,decision_id,"supports")

        return {
            "status":"SYNCED",
            "summary":graph.summary()
        }
