import json
from pathlib import Path
from app.p18_conversational_execution.pilot_flags import load_flags, validate_flags

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P18F_INTERNAL_PILOT_FLAG_DESIGN_20260616_214846")

flags = load_flags()

report = {
    "mission": "P18F_INTERNAL_PILOT_FLAG_DESIGN",
    "status": "PASS" if validate_flags(flags) else "FAIL",
    "flags": flags.__dict__,
    "runtime_modified": False,
    "production_enabled": False,
    "next_required_action": "P18G_INTERNAL_PILOT_DRY_RUN"
}

(out / "P18F_FLAG_REPORT.json").write_text(
    json.dumps(report, indent=2),
    encoding="utf-8"
)

print(json.dumps(report))
