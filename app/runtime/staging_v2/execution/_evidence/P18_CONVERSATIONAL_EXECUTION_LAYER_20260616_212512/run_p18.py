import json
from pathlib import Path
from app.p18_conversational_execution.response_executor import execute_conversational_response

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P18_CONVERSATIONAL_EXECUTION_LAYER_20260616_212512")

cases = [
    "oi",
    "tudo bem?",
    "o que vc esta achando das implementações novas?",
    "cite todos os aspectos significativos",
    "tenho um problema me ajuda",
    "quero o link do youtube de uma musica do metallica",
    "quero que vc procure pra mim e me envie",
]

results = [execute_conversational_response(c) for c in cases]
pass_count = sum(1 for r in results if r["status"] == "PASS")

report = {
    "mission": "P18_CONVERSATIONAL_EXECUTION_LAYER",
    "cases": len(results),
    "pass_count": pass_count,
    "runtime_modified": False,
    "routes_modified": False,
    "dispatcher_modified": False,
    "whatsapp_webhook_modified": False,
    "production_enabled": False,
    "status": "PASS" if pass_count == len(results) else "FAIL",
    "next_required_action": "P18B_RUNTIME_HOOK_DESIGN",
    "results": results,
}

(out / "P18_CONVERSATIONAL_EXECUTION_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
