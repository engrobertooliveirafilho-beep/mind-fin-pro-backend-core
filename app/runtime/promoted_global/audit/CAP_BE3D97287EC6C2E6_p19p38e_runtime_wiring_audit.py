from pathlib import Path
import json
import os
import re
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38E_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    {
        "id": "safe_recovery_adapter",
        "path": "app/companionship/safe_recovery_adapter.py",
        "risk": "MEDIUM",
        "purpose": "central context collector already used for shadow memory",
    },
    {
        "id": "whatsapp_runtime",
        "path": "app/api/whatsapp.py",
        "risk": "HIGH",
        "purpose": "production WhatsApp entrypoint",
    },
    {
        "id": "cognitive_pipeline",
        "path": "app/runtime/cognitive_pipeline.py",
        "risk": "HIGH",
        "purpose": "runtime cognition pipeline",
    },
    {
        "id": "live_cognition_gated",
        "path": "app/companionship/live_cognition_gated.py",
        "risk": "MEDIUM",
        "purpose": "feature-flagged live cognition gate",
    },
    {
        "id": "digital_twin_real",
        "path": "app/companionship/digital_twin_real.py",
        "risk": "MEDIUM",
        "purpose": "digital twin shadow profile",
    },
    {
        "id": "long_term_memory_real",
        "path": "app/companionship/long_term_memory_real.py",
        "risk": "MEDIUM",
        "purpose": "long-term memory consolidation",
    },
    {
        "id": "self_reflection_engine",
        "path": "app/companionship/self_reflection_engine.py",
        "risk": "MEDIUM",
        "purpose": "self reflection readiness",
    },
]

def read(path):
    p = ROOT / path
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def function_names(text):
    return re.findall(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", text, flags=re.M)

def import_lines(text):
    return [line for line in text.splitlines() if line.strip().startswith(("import ", "from "))]

def has_token(text, token):
    return token in text

audits = []

for t in TARGETS:
    text = read(t["path"])
    exists = bool(text)
    funcs = function_names(text)
    imports = import_lines(text)

    anchors = []
    for token in [
        "collect_recovered_context",
        "record_shadow_telemetry",
        "webhook",
        "Body",
        "From",
        "MessageSid",
        "cognitive",
        "respond",
        "pipeline",
        "attach_live_cognition_shadow",
        "attach_digital_twin_shadow",
        "attach_long_term_memory_shadow",
        "attach_self_reflection_shadow",
    ]:
        if token in text:
            anchors.append(token)

    current_connections = {
        "imports_live_cognition_gated": "live_cognition_gated" in text,
        "imports_digital_twin_real": "digital_twin_real" in text,
        "imports_long_term_memory_real": "long_term_memory_real" in text,
        "imports_self_reflection_engine": "self_reflection_engine" in text,
        "mentions_safe_recovery_adapter": "safe_recovery_adapter" in text or "collect_recovered_context" in text,
        "mentions_shadow": "SHADOW_ONLY" in text or "shadow" in text.lower(),
        "mentions_feature_flag": "os.getenv" in text or "P19P37" in text or "P19P36" in text,
    }

    suggested_patch = []

    if t["id"] == "safe_recovery_adapter":
        suggested_patch = [
            "import attach_digital_twin_shadow",
            "import attach_behavior_model_shadow",
            "import attach_emotional_continuity_shadow",
            "import attach_long_term_memory_shadow",
            "import attach_self_reflection_shadow",
            "import attach_live_cognition_shadow",
            "attach in collect_recovered_context after p19p36p_long_term_goal_shadow",
            "record in telemetry payload",
        ]

    if t["id"] == "whatsapp_runtime":
        suggested_patch = [
            "do not modify directly until adapter wiring has tests",
            "audit only for collect_recovered_context usage",
            "promote only with feature flag and canary allowlist",
        ]

    if t["id"] == "cognitive_pipeline":
        suggested_patch = [
            "do not modify directly until safe_recovery_adapter emits full cognition shadow",
            "read cognition context only after no response regression",
            "compare shadow-vs-visible output before promotion",
        ]

    audits.append({
        **t,
        "exists": exists,
        "size": (ROOT / t["path"]).stat().st_size if exists else 0,
        "functions": funcs,
        "imports_count": len(imports),
        "anchors": anchors,
        "current_connections": current_connections,
        "suggested_patch": suggested_patch,
        "recommended_action": (
            "WIRE_IN_SAFE_RECOVERY_ADAPTER_FIRST"
            if t["id"] == "safe_recovery_adapter"
            else "AUDIT_ONLY_DO_NOT_PATCH_DIRECTLY"
            if t["id"] in ["whatsapp_runtime", "cognitive_pipeline"]
            else "AVAILABLE_FOR_ADAPTER_IMPORT"
            if exists
            else "CREATE_OR_RESTORE"
        ),
    })

blocking = []
for a in audits:
    if not a["exists"]:
        blocking.append({"id": a["id"], "reason": "missing_file", "path": a["path"]})

safe_first_step = [
    "Patch only app/companionship/safe_recovery_adapter.py",
    "Attach P19P37 shadows after existing P19P36 shadows",
    "Do not alter app/api/whatsapp.py",
    "Do not alter app/runtime/cognitive_pipeline.py",
    "Keep P19P37_LIVE_COGNITION_ENABLED default false",
    "Add telemetry only",
    "Run focused tests before any commit",
]

summary = {
    "mission": "P19P38_E_RUNTIME_WIRING_AUDIT",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "targets_total": len(audits),
    "targets_missing": len(blocking),
    "high_risk_targets": sum(1 for a in audits if a["risk"] == "HIGH"),
    "safe_first_step": "safe_recovery_adapter_only",
    "direct_whatsapp_patch_allowed": False,
    "direct_cognitive_pipeline_patch_allowed": False,
}

(OUT / "runtime_wiring_audit.json").write_text(json.dumps(audits, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "safe_first_step.json").write_text(json.dumps(safe_first_step, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# P19P38-E Runtime Wiring Audit")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## Targets")
for a in audits:
    md.append(f"- {a['id']} | exists={a['exists']} | risk={a['risk']} | action={a['recommended_action']}")
md.append("")
md.append("## Safe First Step")
for s in safe_first_step:
    md.append(f"- {s}")
md.append("")
md.append("## Blocking")
for b in blocking:
    md.append(f"- {b['id']} | {b['reason']} | {b['path']}")
md.append("")
md.append("## Rule")
md.append("- No runtime wiring applied")
md.append("- No WhatsApp direct patch")
md.append("- No cognitive_pipeline direct patch")
md.append("- Audit only")
md.append("")
md.append("## Next")
md.append("P19P38-F Production Candidate Map OR P19P39 Adapter-Only Shadow Wiring")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
