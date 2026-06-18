from __future__ import annotations
from app.modules.usde_core.red_team_engine import RedTeamEngine

class RedTeamService:
    def run(self,decision:dict,evidence:dict|None=None,metadata:dict|None=None):
        result=RedTeamEngine().audit(
            decision,
            evidence or {},
            metadata or {}
        )

        return {
            "status":"COMPLETED",
            "red_team_status":result["status"],
            "severity":result["severity"],
            "flags":result["flags"]
        }
