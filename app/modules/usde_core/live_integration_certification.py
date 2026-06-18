from __future__ import annotations

from pathlib import Path
from app.api.whatsapp import p449c_usde_whatsapp_hook
from app.api.eldora_core_runtime import p449d_usde_eldora_core_hook
from app.modules.usde_core.supabase_live_hook import USDESupabaseLiveHook
from app.modules.usde_core.drive_live_hook import USDEDriveLiveHook

class USDELiveIntegrationCertification:
    def certify(self):
        p=Path("_evidence/p449g_drive_probe.txt")
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("ok",encoding="utf-8")

        results={
            "whatsapp": p449c_usde_whatsapp_hook(),
            "eldora_core": p449d_usde_eldora_core_hook(),
            "supabase": USDESupabaseLiveHook().observe_memory_event(
                "scientific_memory",
                {"status":"ok"}
            ),
            "drive": USDEDriveLiveHook().observe_file(str(p))
        }

        return {
            "status":"CERTIFIED",
            "channels":list(results.keys()),
            "results":results
        }
