from __future__ import annotations
from app.modules.usde_core.scientific_background_service import ScientificBackgroundService
from app.modules.usde_core.runtime_health_monitor import RuntimeHealthMonitor

class AutonomousDiscoveryLoop:
    def run_once(self,dataset_profile:dict):
        health=RuntimeHealthMonitor().check(
            {"runtime_status":"ONLINE","modules":27}
        )

        if health["status"]!="HEALTHY":
            return {
                "status":"ABORTED",
                "reason":"RUNTIME_NOT_HEALTHY",
                "health":health
            }

        result=ScientificBackgroundService().start(
            dataset_profile
        )

        return {
            "status":"COMPLETED",
            "health":health,
            "result":result
        }
