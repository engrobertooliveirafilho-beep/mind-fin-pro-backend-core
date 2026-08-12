import json, pathlib
p=pathlib.Path(r"_evidence\P19P38_G_WORKTREE_FORENSIC_AUDIT_20260622_175741")/"summary.json"
s=json.loads(p.read_text(encoding="utf-8"))
assert s["status"]=="AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["files_moved"] is False
assert s["files_deleted"] is False
print("P19P38_G_ASSERTIONS_PASS")
