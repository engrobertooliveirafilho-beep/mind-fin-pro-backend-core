import json
from pathlib import Path
from app.p18_conversational_execution.response_executor import execute_conversational_response
from app.p18_conversational_execution.shadow_diff import compare_runtime_vs_shadow

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P18C_SHADOW_VS_RUNTIME_DIFF_20260616_213701")

cases = [
    ["tenho um problema me ajuda", {"answer": "Claro! Para ajudar você, vamos seguir algumas etapas em um checklist."}],
    ["quero o link do youtube de uma musica do metallica", {"answer": "Passo 1: escolher a música. Passo 2: acessar o YouTube."}],
    ["cite todos os aspectos significativos", {"answer": "Para abordar a solicitação, é importante considerar diferentes áreas e contextos."}],
]

results = []
for message, runtime_response in cases:
    candidate = execute_conversational_response(message)
    results.append(compare_runtime_vs_shadow(message, runtime_response, {"answer": candidate["answer"]}))

better_count = sum(1 for r in results if r["candidate_better"])

report = {
    "mission": "P18C_SHADOW_VS_RUNTIME_DIFF",
    "cases": len(results),
    "candidate_better_count": better_count,
    "runtime_modified": False,
    "runtime_response_modified": False,
    "production_enabled": False,
    "status": "PASS" if better_count == len(results) else "REVIEW",
    "next_required_action": "P18D_LIMITED_INTERNAL_SELECTION_GATE",
    "results": results,
}

(out / "P18C_SHADOW_VS_RUNTIME_DIFF_REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
