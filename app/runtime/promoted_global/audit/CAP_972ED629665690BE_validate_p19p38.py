import json
import pathlib

p = pathlib.Path(r"_evidence\P19P38_REPOSITORY_SANITIZATION_AND_COGNITION_BASELINE_20260622_141617") / "summary.json"

s = json.loads(
    p.read_text(encoding="utf-8")
)

assert s["status"] == "AUDIT_ONLY_PASS"
assert s["runtime_modified"] is False
assert s["files_deleted"] is False

print("P19P38_ASSERTIONS_PASS")
