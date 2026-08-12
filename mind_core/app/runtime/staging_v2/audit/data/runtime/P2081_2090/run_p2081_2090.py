import json

from app.runtime.p2081_2090_realtime_portfolio_governance import run_p2081_2090

result = run_p2081_2090(
    portfolio_path="data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json",
    p2071_certification_path="data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json",
    output_dir="data/runtime/P2081_2090/evidence",
)

print(json.dumps(result, indent=2, ensure_ascii=False))
