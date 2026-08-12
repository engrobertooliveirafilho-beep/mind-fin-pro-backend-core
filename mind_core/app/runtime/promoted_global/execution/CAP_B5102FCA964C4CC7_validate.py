import json, pathlib
p=pathlib.Path(r"_evidence\P19P38_K_CRITICAL_DIFF_RESOLUTION_PLAN_20260622_182307")/"summary.json"
s=json.loads(p.read_text(encoding="utf-8"))
assert s["status"]=="DRY_RUN_PLAN_ONLY"
assert s["runtime_modified"] is False
assert s["files_moved"] is False
assert s["files_deleted"] is False
assert s["hunks_total"] >= 1
print("P19P38_K_ASSERTIONS_PASS")
