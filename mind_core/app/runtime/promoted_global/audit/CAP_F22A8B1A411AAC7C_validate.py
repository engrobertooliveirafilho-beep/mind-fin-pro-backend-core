import json, pathlib
p=pathlib.Path(r"_evidence\P19P38_J_CRITICAL_RUNTIME_MANUAL_REVIEW_20260622_181851")/"summary.json"
s=json.loads(p.read_text(encoding="utf-8"))
assert s["status"]=="AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["files_moved"] is False
assert s["files_deleted"] is False
assert s["hunks_total"] >= 1
print("P19P38_J_ASSERTIONS_PASS")
