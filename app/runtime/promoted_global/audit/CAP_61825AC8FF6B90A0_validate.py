import json, pathlib
p=pathlib.Path(r"_evidence\P19P38_C_ORPHAN_MODULE_CLASSIFICATION_20260622_143129")/"summary.json"
s=json.loads(p.read_text(encoding="utf-8"))
assert s["status"]=="AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["files_moved"] is False
assert s["files_deleted"] is False
assert s["candidate_count"] >= 1
print("P19P38_C_ASSERTIONS_PASS")
