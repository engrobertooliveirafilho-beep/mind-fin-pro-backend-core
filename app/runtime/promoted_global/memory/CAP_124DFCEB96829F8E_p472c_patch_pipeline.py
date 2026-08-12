from pathlib import Path

p = Path("app/runtime/cognitive_pipeline.py")
s = p.read_text(encoding="utf-8")

if "P4.72C_CAPABILITY_AUX_REPORT" in s:
    print("PIPELINE_PATCH_ALREADY_PRESENT")
    raise SystemExit(0)

# Inject aux near the start after def and retrieval bridge area if possible.
target = '''    from app.persona.eldora_core import build_persona_context
'''

insert = '''    # P4.72C_CAPABILITY_AUX_REPORT
    capability_aux_report = None
    try:
        from app.runtime.capability_recovery_bridge import capability_recovery_report
        capability_aux_report = capability_recovery_report(user_id, message)
    except Exception:
        capability_aux_report = None

    from app.persona.eldora_core import build_persona_context
'''

if target not in s:
    raise SystemExit("TARGET_IMPORT_NOT_FOUND")

s = s.replace(target, insert, 1)

# Add capabilities field to direct retrieval returns
s = s.replace(
'''                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},''',
'''                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector"},
                        "capabilities": capability_aux_report,''',
)

s = s.replace(
'''                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector_or_rest"},''',
'''                        "retrieval": {"used": True, "rows": len(semantic_retrieval_rows), "mode": "pgvector_or_rest"},
                            "capabilities": capability_aux_report,''',
)

# Add to generic final dict if exact pattern exists
s = s.replace(
'''        "relationship": relationship,''',
'''        "relationship": relationship,
        "capabilities": capability_aux_report,''',
)

p.write_text(s, encoding="utf-8")
print("PIPELINE_PATCH_APPLIED_OK")
