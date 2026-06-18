from __future__ import annotations
import time

from app.modules.usde_core.autonomous_scientific_pipeline import AutonomousScientificPipeline

class ScientificSchedulerRuntime:
    def run_cycle(self,dataset_profile:dict):
        started=time.time()

        result=AutonomousScientificPipeline().run(
            dataset_profile
        )

        return {
            "status":"COMPLETED",
            "started":started,
            "finished":time.time(),
            "executed":result["executed"]
        }
