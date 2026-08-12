import json
from app.runtime.p2111_2120_maximum_technical_capacity import run_p2111_2120

result = run_p2111_2120(
    repo=".",
    portfolio_path="data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json",
    p2071_certification_path="data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json",
    p2081_certification_path="data/runtime/P2081_2090/evidence/P2081_2090_FINAL_CERTIFICATION.json",
    p2091_certification_path="data/runtime/P2091_2100/evidence/P2091_2100_FINAL_CERTIFICATION.json",
    p2101_certification_path="data/runtime/P2101_2110/evidence/P2101_2110_FINAL_CERTIFICATION.json",
    output_dir="data/runtime/P2111_2120/evidence",
)

print(json.dumps(result, indent=2, ensure_ascii=False))
