import json

from app.runtime.p2121_plus_continuous_max_capacity_audit import run_p2121_plus

deps = {
    "portfolio": "data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json",
    "p2071": "data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json",
    "p2081": "data/runtime/P2081_2090/evidence/P2081_2090_FINAL_CERTIFICATION.json",
    "p2091": "data/runtime/P2091_2100/evidence/P2091_2100_FINAL_CERTIFICATION.json",
    "p2101": "data/runtime/P2101_2110/evidence/P2101_2110_FINAL_CERTIFICATION.json",
    "p2111": "data/runtime/P2111_2120/evidence/P2111_2120_FINAL_CERTIFICATION.json",
}

result = run_p2121_plus(
    repo=".",
    dependencies=deps,
    output_dir="data/runtime/P2121_PLUS/evidence",
)

print(json.dumps(result, indent=2, ensure_ascii=False))
