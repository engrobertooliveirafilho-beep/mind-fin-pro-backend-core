import json
from pathlib import Path
from app.p16_real_use_case.response_modification_safety_gate import run_response_modification_safety_gate

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P16F_RESPONSE_MODIFICATION_SAFETY_GATE_20260616_161735")
result = run_response_modification_safety_gate()

(out / "P16F_RESPONSE_MODIFICATION_SAFETY_GATE_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
