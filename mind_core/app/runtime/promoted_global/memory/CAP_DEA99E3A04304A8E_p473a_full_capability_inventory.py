import json
import importlib
import inspect
from pathlib import Path

MODULES=[
"app.eldora.core.persistent_social_memory",
"app.persona.adaptive_social_dialogue",
"app.api.eldora_social",
"app.retrieval.provider",
"app.eldora.core.long_term_memory",
"app.eldora.core.visual_semantic_memory",
"app.eldora.core.persistent_cognitive_graph",
"app.eldora.core.memory_compression_engine",
"app.eldora.core.session_memory",
"app.memory.provider",
"app.modules.usde_core.supabase_scientific_memory",
"app.runtime.memory_store",
"app.persona.persona_continuity_memory",
"app.vision.vision_memory_store",
"app.eldora.core.service_health_graph",
"app.modules.usde_core.scientific_knowledge_graph",
"app.persona.emotional_dialogue_layer",
"app.admin.semantic_activation",
"app.runtime.semantic_whatsapp_runtime",
"app.api.eldora_semantic",
"app.eldora.core.emotional_continuity_engine",
"app.ingestion.semantic_chunking"
]

report=[]

for name in MODULES:

    row={
        "module":name,
        "import_ok":False,
        "functions":[],
        "classes":[],
        "classification":"UNKNOWN",
        "reason":""
    }

    try:

        m=importlib.import_module(name)

        row["import_ok"]=True

        funcs=[]
        classes=[]

        for attr in dir(m):

            obj=getattr(m,attr)

            if inspect.isfunction(obj):
                funcs.append(attr)

            elif inspect.isclass(obj):
                classes.append(attr)

        row["functions"]=sorted(funcs)
        row["classes"]=sorted(classes)

        score=len(funcs)+len(classes)

        if score >= 10:
            row["classification"]="READY_TO_INTEGRATE"

        elif score >= 5:
            row["classification"]="NEEDS_ADAPTER"

        elif score > 0:
            row["classification"]="ORPHAN"

        else:
            row["classification"]="DEPRECATED"

    except Exception as e:

        row["classification"]="BROKEN"
        row["reason"]=str(e)

    report.append(row)

summary={}

for r in report:
    c=r["classification"]
    summary[c]=summary.get(c,0)+1

payload={
    "summary":summary,
    "modules":report
}

Path("capability_inventory.json").write_text(
    json.dumps(payload,indent=2,ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(summary,indent=2))
