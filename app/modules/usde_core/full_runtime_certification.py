from __future__ import annotations
import json,time
from pathlib import Path

from app.modules.usde_core.scientific_os import ScientificOS
from app.modules.usde_core.runtime_health_monitor import RuntimeHealthMonitor
from app.modules.usde_core.autonomous_discovery_loop import AutonomousDiscoveryLoop

class FullRuntimeCertification:
    def certify(self):
        boot=ScientificOS().boot()
        health=RuntimeHealthMonitor().check(
            {"runtime_status":"ONLINE","modules":boot["module_count"]}
        )
        loop=AutonomousDiscoveryLoop().run_once(
            {"events":1000,"temporal":True,"graph":True,"symbolic":True,"automl":True}
        )

        status=(
            "CERTIFIED"
            if boot["status"]=="ONLINE"
            and health["status"]=="HEALTHY"
            and loop["status"]=="COMPLETED"
            else "FAILED"
        )

        result={
            "mission":"P4.47Z_FULL_RUNTIME_CERTIFICATION",
            "timestamp":time.time(),
            "status":status,
            "boot":boot,
            "health":health,
            "loop":loop
        }

        out=Path("_evidence/P4.47Z_FULL_CERTIFICATION")
        out.mkdir(parents=True,exist_ok=True)
        (out/"certification.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2),
            encoding="utf-8"
        )

        return result
