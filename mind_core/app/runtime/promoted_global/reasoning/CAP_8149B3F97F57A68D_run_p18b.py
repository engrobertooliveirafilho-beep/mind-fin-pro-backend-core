import json
from pathlib import Path
from app.p18_conversational_execution.runtime_hook import run_p18_runtime_hook_shadow

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P18B_RUNTIME_HOOK_DESIGN_20260616_213031")

cases = [
    ["tenho um problema me ajuda", {"answer": "Vamos seguir algumas etapas..."}],
    ["quero o link do youtube de uma musica do metallica", {"answer": "Passo 1..."}],
    ["cite todos os aspectos significativos", {"answer": "Para abordar..."}],
]

results = [run_p18_runtime_hook_shadow(m, r) for m, r in cases]
pass_count = sum(1 for r in results if r["status"] == "PASS")

report = {
    "mission": "P18B_RUNTIME_HOOK_DESIGN",
    "cases": len(results),
    "pass_count": pass_count,
    "runtime_modified": False,
    "runtime_response_modified": False,
    "production_enabled": False,
    "status": "PASS" if pass_count == len(results) else "FAIL",
    "next_required_action": "P18C_SHADOW_VS_RUNTIME_DIFF",
    "results": results
}

(out / "P18B_RUNTIME_HOOK_DESIGN_REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
