import json
from pathlib import Path
from app.p16_real_use_case.controlled_response_shadow import run_controlled_response_modification_shadow

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P16G_CONTROLLED_RESPONSE_MODIFICATION_SHADOW_20260616_162323")
result = run_controlled_response_modification_shadow()

(out / "P16G_CONTROLLED_RESPONSE_MODIFICATION_SHADOW_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
