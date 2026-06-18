from __future__ import annotations

from app.modules.usde_core.hypothesis_registry import HypothesisRegistry
from app.modules.usde_core.experiment_registry import ExperimentRegistry
from app.modules.usde_core.evidence_registry import EvidenceRegistry
from app.modules.usde_core.decision_registry import DecisionRegistry

class ScientificRuntimeOrchestrator:
    def __init__(self):
        self.hypotheses=HypothesisRegistry()
        self.experiments=ExperimentRegistry()
        self.evidence=EvidenceRegistry()
        self.decisions=DecisionRegistry()

    def run(self,name:str,statement:str):
        h=self.hypotheses.register(
            name,
            statement
        )

        e=self.experiments.register(
            name,
            {"hypothesis_id":h["hypothesis_id"]}
        )

        ev=self.evidence.register(
            e["experiment_id"],
            "runtime_execution",
            {"status":"EXECUTED"}
        )

        d=self.decisions.register(
            h["hypothesis_id"],
            "INCONCLUSIVA",
            {"evidence_id":ev["evidence_id"]}
        )

        return {
            "hypothesis":h,
            "experiment":e,
            "evidence":ev,
            "decision":d
        }
