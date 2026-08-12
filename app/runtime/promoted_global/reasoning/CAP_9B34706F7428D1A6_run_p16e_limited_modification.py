import json
from pathlib import Path
from app.p16_real_use_case.limited_response_modification import run_limited_response_modification_dry_run

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P16E_LIMITED_RESPONSE_MODIFICATION_DRY_RUN_20260616_161249")
result = run_limited_response_modification_dry_run()

(out / "P16E_LIMITED_RESPONSE_MODIFICATION_DRY_RUN_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
