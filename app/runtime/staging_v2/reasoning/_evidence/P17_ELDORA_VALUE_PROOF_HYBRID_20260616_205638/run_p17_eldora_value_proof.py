import json
from pathlib import Path
from app.p17_value_proof.eldora_value_proof import run_eldora_value_proof

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P17_ELDORA_VALUE_PROOF_HYBRID_20260616_205638")
result = run_eldora_value_proof()

(out / "P17_ELDORA_VALUE_PROOF_HYBRID_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

summary = {
    "mission": result["mission"],
    "status": result["status"],
    "cases": result["cases"],
    "pass_count": result["pass_count"],
    "avg_baseline_score": result["avg_baseline_score"],
    "avg_planner_score": result["avg_planner_score"],
    "avg_gain_pct": result["avg_gain_pct"],
    "recommendation": result["recommendation"],
    "production_enabled": result["production_enabled"],
    "runtime_modified": result["runtime_modified"],
}

(out / "P17_ELDORA_VALUE_PROOF_SUMMARY.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(summary, ensure_ascii=False))
