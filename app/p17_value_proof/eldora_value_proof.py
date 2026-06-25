from typing import Dict, Any, List
from app.p8_shadow.real_planner import generate_hierarchical_plan

ELDORA_CASES = [
    {"id": "E01", "topic": "Treino Emagrecimento", "input": "Quero perder 12 kg até dezembro."},
    {"id": "E02", "topic": "Treino Feminino", "input": "Quero aumentar glúteo e diminuir barriga."},
    {"id": "E03", "topic": "Treino Casa", "input": "Só tenho halteres em casa."},
    {"id": "E04", "topic": "Dieta Simples", "input": "Tenho pouco dinheiro para dieta."},
    {"id": "E05", "topic": "Faculdade", "input": "Estou perdido em cálculo 1."},
    {"id": "E06", "topic": "Concurso", "input": "Como organizar meus estudos para concurso?"},
    {"id": "E07", "topic": "Inglês", "input": "Quero aprender inglês do zero."},
    {"id": "E08", "topic": "Motivação", "input": "Estou sem disciplina para treinar."},
    {"id": "E09", "topic": "Rotina", "input": "Como organizar trabalho, treino e estudo?"},
    {"id": "E10", "topic": "Ansiedade", "input": "Estou muito ansioso com minha vida."},
    {"id": "E11", "topic": "Instagram", "input": "Quero crescer meu Instagram."},
    {"id": "E12", "topic": "TikTok", "input": "Meu TikTok não cresce."},
    {"id": "E13", "topic": "Finanças", "input": "Como sair das dívidas?"},
    {"id": "E14", "topic": "Carreira", "input": "Quero ganhar mais dinheiro."},
    {"id": "E15", "topic": "Empreendedorismo", "input": "Quero abrir um negócio."},
    {"id": "E16", "topic": "Relacionamento", "input": "Minha esposa não apoia meus projetos."},
    {"id": "E17", "topic": "Faculdade + Trabalho", "input": "Trabalho o dia inteiro e estudo à noite."},
    {"id": "E18", "topic": "Autoestima", "input": "Não consigo acreditar em mim."},
    {"id": "E19", "topic": "Organização", "input": "Minha vida está uma bagunça."},
    {"id": "E20", "topic": "Objetivo de Vida", "input": "Não sei o que fazer da minha vida."},
]

def baseline_response(case: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "answer": f"Entendi. Vamos organizar isso com calma: {case['input']}",
        "steps": ["entender objetivo", "definir prioridade", "começar com uma ação simples"],
        "depth": 1,
        "tone": "generic_supportive",
    }

def planner_response(case: Dict[str, Any]) -> Dict[str, Any]:
    plan = generate_hierarchical_plan({
        "goal": case["input"],
        "topic": case["topic"],
        "persona": "Eldora"
    })

    return {
        "answer": f"Vamos transformar isso em plano: {case['input']}",
        "planner": plan,
        "steps": plan["plan"],
        "depth": plan["depth"],
        "tone": "structured_supportive",
    }

def heuristic_score(response: Dict[str, Any]) -> Dict[str, Any]:
    steps = response.get("steps", [])
    depth = int(response.get("depth", 1))

    actionable_steps = len(steps)
    structure_score = min(10, actionable_steps * 1.2)
    depth_score = min(10, depth * 2.5)
    clarity_score = 8 if response.get("answer") else 0
    completeness_score = min(10, structure_score * 0.6 + depth_score * 0.4)

    total = round((structure_score + depth_score + clarity_score + completeness_score) / 4, 2)

    return {
        "structure_score": round(structure_score, 2),
        "depth_score": round(depth_score, 2),
        "clarity_score": round(clarity_score, 2),
        "completeness_score": round(completeness_score, 2),
        "heuristic_total": total,
    }

def llm_judge_proxy(case: Dict[str, Any], base: Dict[str, Any], planner: Dict[str, Any]) -> Dict[str, Any]:
    base_steps = len(base.get("steps", []))
    planner_steps = len(planner.get("steps", []))
    base_depth = int(base.get("depth", 1))
    planner_depth = int(planner.get("depth", 1))

    goal_coverage = min(10, 5 + (planner_steps - base_steps) * 0.8)
    actionability = min(10, 5 + planner_steps * 0.7)
    execution_order = 9 if planner_depth >= 3 else 6
    user_value = round((goal_coverage + actionability + execution_order) / 3, 2)

    return {
        "judge_type": "LLM_JUDGE_PROXY_HEURISTIC",
        "goal_coverage": round(goal_coverage, 2),
        "actionability": round(actionability, 2),
        "execution_order": round(execution_order, 2),
        "user_value": user_value,
        "note": "Proxy local. Substituir por LLM-as-Judge real quando API/judge estiver disponível.",
    }

def run_eldora_value_proof() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for case in ELDORA_CASES:
        base = baseline_response(case)
        planner = planner_response(case)

        base_h = heuristic_score(base)
        planner_h = heuristic_score(planner)
        judge = llm_judge_proxy(case, base, planner)

        baseline_total = base_h["heuristic_total"]
        planner_total = round((planner_h["heuristic_total"] * 0.55) + (judge["user_value"] * 0.45), 2)

        gain_abs = round(planner_total - baseline_total, 2)
        gain_pct = round((gain_abs / baseline_total) * 100, 2) if baseline_total > 0 else 0

        results.append({
            "id": case["id"],
            "topic": case["topic"],
            "input": case["input"],
            "baseline_score": baseline_total,
            "planner_score": planner_total,
            "gain_abs": gain_abs,
            "gain_pct": gain_pct,
            "baseline_heuristic": base_h,
            "planner_heuristic": planner_h,
            "judge_proxy": judge,
            "runtime_modified": False,
            "production_enabled": False,
            "real_user_sent": False,
            "status": "PASS" if gain_abs > 0 else "REVIEW",
        })

    avg_baseline = round(sum(r["baseline_score"] for r in results) / len(results), 2)
    avg_planner = round(sum(r["planner_score"] for r in results) / len(results), 2)
    avg_gain_abs = round(avg_planner - avg_baseline, 2)
    avg_gain_pct = round((avg_gain_abs / avg_baseline) * 100, 2) if avg_baseline > 0 else 0
    pass_count = sum(1 for r in results if r["status"] == "PASS")

    return {
        "mission": "P17_ELDORA_VALUE_PROOF_HYBRID",
        "cases": len(results),
        "pass_count": pass_count,
        "avg_baseline_score": avg_baseline,
        "avg_planner_score": avg_planner,
        "avg_gain_abs": avg_gain_abs,
        "avg_gain_pct": avg_gain_pct,
        "method": {
            "type": "HYBRID",
            "heuristic_weight": 0.55,
            "judge_proxy_weight": 0.45,
            "llm_judge_real": False,
        },
        "runtime_modified": False,
        "production_enabled": False,
        "real_user_sent": False,
        "recommendation": "KEEP_PLANNER_INTERNAL_AND_PREPARE_REAL_LLM_JUDGE" if avg_gain_pct > 15 else "KEEP_SHADOW_AND_IMPROVE_PLANNER",
        "next_required_action": "P17B_REAL_LLM_JUDGE_OR_HUMAN_REVIEW",
        "status": "PASS" if pass_count >= 16 and avg_gain_pct > 15 else "REVIEW",
        "results": results,
    }
