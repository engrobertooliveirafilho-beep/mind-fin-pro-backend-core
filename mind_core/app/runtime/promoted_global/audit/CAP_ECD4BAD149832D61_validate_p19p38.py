import json
import pathlib

p = pathlib.Path(r"_evidence\P19P36P_C_GOAL_PROGRESS_ADVISOR_20260622_133231") / "summary.json"

s = json.loads(
    p.read_text(encoding="utf-8")
)

assert s["status"] == "AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["files_deleted"] is False

print("P19P38_ASSERTIONS_PASS")
