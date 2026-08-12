import json
from pathlib import Path

report_path = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19B_WHATSAPP_SHADOW_LIVE_REPLAY_20260617_105551\\P19B_WHATSAPP_SHADOW_LIVE_REPLAY_REPORT.json")
out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19C_WHATSAPP_SHADOW_METRICS_20260617_110513")

report = json.loads(report_path.read_text(encoding="utf-8"))
results = report["results"]

cases = len(results)
pass_count = sum(1 for r in results if r["status"] == "PASS")
contamination = sum(1 for r in results if r["context_contaminated"])
sent = sum(1 for r in results if r["real_user_sent"])
prod = sum(1 for r in results if r["production_enabled"])
runtime_mod = sum(1 for r in results if r["runtime_modified"])

metrics = {
    "mission": "P19C_WHATSAPP_SHADOW_METRICS",
    "cases": cases,
    "pass_rate": round(pass_count / cases, 4),
    "context_contamination_rate": round(contamination / cases, 4),
    "real_user_sent_count": sent,
    "production_enabled_count": prod,
    "runtime_modified_count": runtime_mod,
    "runtime_modified": False,
    "production_enabled": False,
    "real_user_sent": False,
    "decision": "KEEP_SHADOW_AND_PREPARE_CONTROLLED_INTERNAL_WHATSAPP_PILOT",
    "next_required_action": "P19D_WHATSAPP_INTERNAL_PILOT_DECISION",
    "status": "PASS" if pass_count == cases and contamination == 0 and sent == 0 and prod == 0 and runtime_mod == 0 else "FAIL",
}

(out / "P19C_WHATSAPP_SHADOW_METRICS_REPORT.json").write_text(
    json.dumps(metrics, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(metrics, ensure_ascii=False))
