import json, pathlib
p=pathlib.Path(r"_evidence\P19P38_E_RUNTIME_WIRING_AUDIT_20260622_144749")/"summary.json"
s=json.loads(p.read_text(encoding="utf-8"))
assert s["status"]=="AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["direct_whatsapp_patch_allowed"] is False
assert s["direct_cognitive_pipeline_patch_allowed"] is False
print("P19P38_E_ASSERTIONS_PASS")
