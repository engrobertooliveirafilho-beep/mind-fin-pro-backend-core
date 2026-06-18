from __future__ import annotations
from app.modules.usde_core.evidence_engine import EvidenceEngine
from app.modules.usde_core.evidence_registry import EvidenceRegistry

class ScientificEvidenceService:
    def run(self,decision:dict,metadata:dict|None=None):
        evidence=EvidenceEngine().score(
            decision,
            metadata=metadata or {}
        )

        record=EvidenceRegistry().register(
            metadata.get("experiment_id","UNKNOWN") if metadata else "UNKNOWN",
            "scientific_evidence",
            evidence
        )

        return {
            "status":"COMPLETED",
            "evidence":evidence,
            "evidence_id":record["evidence_id"]
        }
