import json, pathlib
p=pathlib.Path(r"_evidence\P19P38_F_PRODUCTION_CANDIDATE_MAP_20260622_175339")/"summary.json"
s=json.loads(p.read_text(encoding="utf-8"))
assert s["status"]=="AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["files_moved"] is False
assert s["files_deleted"] is False
assert s["candidates_total"] >= 5
print("P19P38_F_ASSERTIONS_PASS")
