import json
from pathlib import Path
from app.p16_real_use_case.response_awareness_quality import run_response_awareness_quality_benchmark

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P16D_RESPONSE_AWARENESS_QUALITY_BENCHMARK_20260616_161008")
result = run_response_awareness_quality_benchmark()

(out / "P16D_RESPONSE_AWARENESS_QUALITY_BENCHMARK_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
