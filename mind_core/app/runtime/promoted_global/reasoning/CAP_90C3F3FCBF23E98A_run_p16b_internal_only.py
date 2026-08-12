import json
from pathlib import Path
from app.p16_real_use_case.internal_only_consumption import run_internal_only_use_cases

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P16B_INTERNAL_ONLY_RUNTIME_CONSUMPTION_TEST_20260616_160204")
result = run_internal_only_use_cases()

(out / "P16B_INTERNAL_ONLY_RUNTIME_CONSUMPTION_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
