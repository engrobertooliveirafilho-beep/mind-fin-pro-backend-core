import json
from pathlib import Path
from app.p18_conversational_execution.selection_gate import run_limited_internal_selection_gate

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P18D_LIMITED_INTERNAL_SELECTION_GATE_20260616_214148")

cases = [
    ["tenho um problema me ajuda", {"answer": "Claro! Para ajudar você, vamos seguir algumas etapas em um checklist."}],
    ["quero o link do youtube de uma musica do metallica", {"answer": "Passo 1: escolher a música. Passo 2: acessar o YouTube."}],
    ["cite todos os aspectos significativos", {"answer": "Para abordar a solicitação, é importante considerar diferentes áreas e contextos."}],
]

results = [run_limited_internal_selection_gate(m, r) for m, r in cases]
candidate_recommendations = sum(1 for r in results if r["recommendation"] == "USE_CANDIDATE_INTERNAL_ONLY")

report = {
    "mission": "P18D_LIMITED_INTERNAL_SELECTION_GATE",
    "cases": len(results),
    "candidate_recommendations": candidate_recommendations,
    "runtime_modified": False,
    "runtime_response_modified": False,
    "production_enabled": False,
    "status": "PASS" if candidate_recommendations == len(results) else "REVIEW",
    "next_required_action": "P18E_INTERNAL_PILOT_READINESS_REVIEW",
    "results": results,
}

(out / "P18D_SELECTION_GATE_REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
