import json
from pathlib import Path
from app.p16_real_use_case.response_shadow_observation import run_response_shadow_observation

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P16H_RESPONSE_SHADOW_OBSERVATION_20260616_171254")
log = out / "P16H_RESPONSE_SHADOW_OBSERVATION.jsonl"

result = run_response_shadow_observation(str(log), iterations=300)

(out / "P16H_RESPONSE_SHADOW_OBSERVATION_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
