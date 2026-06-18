from __future__ import annotations

class RuntimeIntegrationBinder:
    def map(self):
        return {
            "supabase": [
                "app/eldora/core/persistent_social_memory.py",
                "app/memory/memory_graph.py",
                "app/runtime/short_memory.py",
                "app/retrieval/provider.py",
                "app/telemetry/cloud_telemetry.py"
            ],
            "whatsapp": [
                "app/api/whatsapp.py",
                "app/runtime/semantic_whatsapp_runtime.py",
                "app/runtime/whatsapp_final_output_guard.py"
            ],
            "drive": [
                "app/eldora/drive_os/service.py",
                "app/runtime/text_provider_adapters.py"
            ],
            "runtime": [
                "app/api/eldora_async.py",
                "app/api/eldora_action.py",
                "app/admin/public_runtime.py",
                "app/admin/semantic_activation.py"
            ],
            "eldora": [
                "app/api/eldora_core_runtime.py",
                "app/api/eldora_action.py",
                "app/api/eldora_autonomous.py",
                "app/api/eldora_evolution.py"
            ]
        }

    def bind_plan(self):
        m=self.map()
        return {
            "status":"BIND_PLAN_READY",
            "targets":m,
            "priority":[
                "runtime",
                "eldora",
                "whatsapp",
                "supabase",
                "drive"
            ]
        }
