from __future__ import annotations
from app.modules.usde_core.scientific_scheduler_runtime import ScientificSchedulerRuntime

class ScientificBackgroundService:
    def __init__(self):
        self.status="IDLE"

    def start(self,dataset_profile:dict):
        self.status="RUNNING"

        result=ScientificSchedulerRuntime().run_cycle(
            dataset_profile
        )

        self.status="COMPLETED"

        return {
            "service_status":self.status,
            "executed":result["executed"]
        }
