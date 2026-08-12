import json

from app.runtime.p2071_2080_realtime_paper_runtime import run_p2071_2080

result = run_p2071_2080(
    portfolio_path="data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json",
    output_dir="data/runtime/P2071_2080/evidence",
    cycles=1500,
)

print(json.dumps(result, indent=2, ensure_ascii=False))
