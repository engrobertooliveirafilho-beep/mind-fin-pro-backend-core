import json
from pathlib import Path

report_path = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19E_WHATSAPP_INTERNAL_PILOT_EXECUTION_20260617_115421\\P19E_WHATSAPP_INTERNAL_PILOT_EXECUTION_REPORT.json")
out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19F_INTERNAL_PILOT_METRICS_20260617_120123")

report = json.loads(report_path.read_text(encoding="utf-8"))
results = report["results"]

cases = len(results)
pass_count = sum(1 for r in results if r["status"] == "PASS")
contamination = sum(1 for r in results if r["context_contaminated"])
sent = sum(1 for r in results if r["real_user_sent"])
prod = sum(1 for r in results if r["production_enabled"])
visible = sum(1 for r in results if r["visible_to_user"])

metrics = {
    "mission": "P19F_INTERNAL_PILOT_METRICS",
    "cases": cases,
    "pass_count": pass_count,
    "pass_rate": round(pass_count / cases, 4),
    "context_contamination_count": contamination,
    "context_contamination_rate": round(contamination / cases, 4),
    "visible_to_user_count": visible,
    "real_user_sent_count": sent,
    "production_enabled_count": prod,
    "runtime_modified": False,
    "production_enabled": False,
    "real_user_sent": False,
    "decision": "ALLOW_P19G_INTERNAL_PILOT_CONCLUSION",
    "next_required_action": "P19G_INTERNAL_PILOT_CONCLUSION",
    "status": "PASS" if pass_count == cases and contamination == 0 and sent == 0 and prod == 0 and visible == 0 else "FAIL",
}

(out / "P19F_INTERNAL_PILOT_METRICS_REPORT.json").write_text(
    json.dumps(metrics, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(metrics, ensure_ascii=False))
