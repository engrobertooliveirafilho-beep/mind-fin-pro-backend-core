import json
from pathlib import Path
from app.p17_value_proof.review_decision_aggregation import aggregate_review_decision

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P17C_REVIEW_DECISION_AGGREGATION_20260616_210653")
result = aggregate_review_decision()

(out / "P17C_REVIEW_DECISION_AGGREGATION_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
