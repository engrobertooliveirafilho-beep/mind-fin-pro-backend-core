import json
from pathlib import Path
from app.p17_value_proof.eldora_human_review import create_human_review_packet

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P17B_REAL_LLM_JUDGE_OR_HUMAN_REVIEW_20260616_210127")
result = create_human_review_packet()

(out / "P17B_REVIEW_PACKET.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

summary = {
    "mission": result["mission"],
    "status": result["status"],
    "cases": result["cases"],
    "avg_gain_pct_proxy": result["avg_gain_pct_proxy"],
    "review_mode": result["review_mode"],
    "production_enabled": result["production_enabled"],
    "runtime_modified": result["runtime_modified"],
    "real_user_sent": result["real_user_sent"],
    "auto_activation_allowed": result["auto_activation_allowed"],
    "next_required_action": result["next_required_action"],
}

(out / "P17B_SUMMARY.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(summary, ensure_ascii=False))
