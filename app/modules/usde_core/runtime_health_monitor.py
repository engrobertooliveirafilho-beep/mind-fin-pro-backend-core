from __future__ import annotations
from app.modules.usde_core.runtime_metrics import RuntimeMetrics

class RuntimeHealthMonitor:
    def check(self,metrics:dict|None=None):
        snapshot=RuntimeMetrics().snapshot(metrics or {})

        issues=[]

        if snapshot["runtime_status"]!="ONLINE":
            issues.append("RUNTIME_OFFLINE")

        if snapshot["modules"] < 1:
            issues.append("NO_MODULES_REGISTERED")

        status="HEALTHY" if not issues else "DEGRADED"

        return {
            "status":status,
            "issues":issues,
            "snapshot":snapshot
        }
