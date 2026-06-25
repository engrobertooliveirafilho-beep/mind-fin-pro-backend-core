from app.p18_conversational_execution.selection_gate import run_limited_internal_selection_gate

def run_internal_pilot_dry_run():
    cases = [
        ["tenho um problema me ajuda", {"answer": "Claro! Vamos seguir algumas etapas em um checklist."}],
        ["quero o link do youtube de uma musica do metallica", {"answer": "Passo 1: escolher a música. Passo 2: acessar o YouTube."}],
        ["cite todos os aspectos significativos", {"answer": "Para abordar a solicitação, é importante considerar diferentes áreas e contextos."}],
    ]

    results = []
    for message, runtime_response in cases:
        gate = run_limited_internal_selection_gate(message, runtime_response)
        results.append({
            "message": message,
            "recommendation": gate["recommendation"],
            "selected_response": gate["selected_response"],
            "candidate_response": gate["candidate_response"],
            "candidate_visible_to_user": False,
            "runtime_response_modified": False,
            "production_enabled": False,
            "status": gate["status"],
        })

    candidate_count = sum(1 for r in results if r["recommendation"] == "USE_CANDIDATE_INTERNAL_ONLY")

    return {
        "mission": "P18G_INTERNAL_PILOT_DRY_RUN",
        "cases": len(results),
        "candidate_recommendations": candidate_count,
        "runtime_modified": False,
        "runtime_response_modified": False,
        "production_enabled": False,
        "status": "PASS" if candidate_count == len(results) else "REVIEW",
        "next_required_action": "P18H_INTERNAL_PILOT_OBSERVATION",
        "results": results,
    }
