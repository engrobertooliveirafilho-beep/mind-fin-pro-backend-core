import json
from pathlib import Path

report_path = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19H_WHATSAPP_SANDBOX_REPLY_DRY_RUN_20260617_134246\\P19H_WHATSAPP_SANDBOX_REPLY_DRY_RUN_REPORT.json")
out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P19I_SANDBOX_EVALUATION_20260617_134934")

report = json.loads(report_path.read_text(encoding="utf-8"))
results = report["results"]

bad_patterns = [
    "passo 1", "passo 2", "para abordar", "diferentes áreas",
    "cognição profunda", "detalhe /", "compatibilidade:", "preço:"
]

evaluated = []
for r in results:
    reply = str(r.get("reply", "") or "")
    low = reply.lower()
    bad_hits = [p for p in bad_patterns if p in low]
    ok = bool(reply.strip()) and len(reply) <= 500 and not bad_hits and r.get("twiml_generated") is True
    evaluated.append({
        "input": r.get("input"),
        "reply": reply,
        "bad_hits": bad_hits,
        "twiml_generated": r.get("twiml_generated"),
        "real_user_sent": False,
        "production_enabled": False,
        "status": "PASS" if ok else "REVIEW"
    })

pass_count = sum(1 for e in evaluated if e["status"] == "PASS")
review_count = len(evaluated) - pass_count

final = {
    "mission": "P19I_SANDBOX_EVALUATION",
    "cases": len(evaluated),
    "pass_count": pass_count,
    "review_count": review_count,
    "production_enabled": False,
    "real_user_sent": False,
    "runtime_modified": False,
    "status": "PASS" if review_count == 0 else "REVIEW",
    "next_required_action": "P19J_REAL_WORLD_VALIDATION_CONCLUSION",
    "results": evaluated
}

(out / "P19I_SANDBOX_EVALUATION_REPORT.json").write_text(
    json.dumps(final, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(final, ensure_ascii=False))
