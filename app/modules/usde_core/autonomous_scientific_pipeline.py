from __future__ import annotations

from app.modules.usde_core.auto_hypothesis_generator import AutoHypothesisGenerator
from app.modules.usde_core.scientific_runtime_orchestrator import ScientificRuntimeOrchestrator

class AutonomousScientificPipeline:
    def run(self,dataset_profile:dict):
        hypotheses=AutoHypothesisGenerator().generate(
            dataset_profile
        )

        results=[]

        for h in hypotheses[:5]:
            results.append(
                ScientificRuntimeOrchestrator().run(
                    h["hypothesis_id"],
                    h["statement"]
                )
            )

        return {
            "generated":len(hypotheses),
            "executed":len(results),
            "results":results
        }
