import json
from pathlib import Path
from app.p16_real_use_case.real_use_case_runner import run_real_use_case_consumption

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P16A_REAL_USE_CASE_CONSUMPTION_20260616_155854")
result = run_real_use_case_consumption()

(out / "P16A_REAL_USE_CASE_CONSUMPTION_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
