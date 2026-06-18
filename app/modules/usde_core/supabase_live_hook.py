from __future__ import annotations

from app.modules.usde_core.supabase_scientific_memory import SupabaseScientificMemory
from app.modules.usde_core.live_bridge import USDELiveBridge

class USDESupabaseLiveHook:
    def observe_memory_event(self, table:str, payload:dict):
        memory = SupabaseScientificMemory().upsert(
            table,
            payload
        )

        observation = USDELiveBridge().observe(
            "supabase_memory",
            {
                "type": "memory_event",
                "table": table,
                "status": memory["status"]
            }
        )

        return {
            "memory": memory,
            "observation": observation
        }
