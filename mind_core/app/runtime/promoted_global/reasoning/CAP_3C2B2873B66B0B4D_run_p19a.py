import json
from pathlib import Path
from app.p19_real_world_validation.whatsapp_real_traffic_eval import run_whatsapp_real_traffic_evaluation

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19A_WHATSAPP_REAL_TRAFFIC_EVALUATION_20260617_095724")
result = run_whatsapp_real_traffic_evaluation()

(out / "P19A_WHATSAPP_REAL_TRAFFIC_EVALUATION_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
