from __future__ import annotations
from app.modules.usde_core.scientific_os import ScientificOS
from app.modules.usde_core.scientific_runtime_orchestrator import ScientificRuntimeOrchestrator
from app.modules.usde_core.runtime_health_monitor import RuntimeHealthMonitor

class USDELiveBridge:
    def status(self):
        boot=ScientificOS().boot()
        health=RuntimeHealthMonitor().check(
            {"runtime_status":"ONLINE","modules":boot["module_count"]}
        )

        return {
            "status":"ONLINE" if health["status"]=="HEALTHY" else "DEGRADED",
            "boot":boot,
            "health":health
        }

    def observe(self,source:str,payload:dict):
        return ScientificRuntimeOrchestrator().run(
            f"live_observation_{source}",
            f"USDE live observation from {source}: {payload.get('type','generic')}"
        )
