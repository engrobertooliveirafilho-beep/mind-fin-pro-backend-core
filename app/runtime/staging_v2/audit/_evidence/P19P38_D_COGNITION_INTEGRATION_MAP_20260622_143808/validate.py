import json, pathlib
p=pathlib.Path(r"_evidence\P19P38_D_COGNITION_INTEGRATION_MAP_20260622_143808")/"summary.json"
s=json.loads(p.read_text(encoding="utf-8"))
assert s["status"]=="AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["files_moved"] is False
assert s["files_deleted"] is False
assert s["nodes_total"] >= 5
print("P19P38_D_ASSERTIONS_PASS")
