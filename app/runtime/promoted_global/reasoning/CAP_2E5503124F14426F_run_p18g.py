import json
from pathlib import Path
from app.p18_conversational_execution.internal_pilot import run_internal_pilot_dry_run

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P18G_INTERNAL_PILOT_DRY_RUN_20260616_215317")
result = run_internal_pilot_dry_run()

(out / "P18G_INTERNAL_PILOT_DRY_RUN_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
