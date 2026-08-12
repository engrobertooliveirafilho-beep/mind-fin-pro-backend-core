
import re

STOP = {
    "não","para","como","uma","meu","minha","com","sem","que","dos","das",
    "por","the","and","only","prossiga"
}

def tokens(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9áéíóúàãõâêôç_]+", " ", text)
    return set(x for x in text.split() if len(x) >= 3 and x not in STOP)

def infer_goal_intent(text: str):
    t = tokens(text)

    intent = "assist"
    goal = "resolver_solicitacao_do_usuario"
    required_outputs = ["resposta_final"]
    required_capabilities = ["knowledge_provider", "final_answer_governance"]

    if {"corrigir","erro","falha","bug","diagnosticar","validar"} & t:
        intent = "diagnose_or_validate"
        required_outputs = ["diagnostico", "causa_provavel", "proximo_passo", "resposta_final"]
        required_capabilities = ["diagnostic", "knowledge_provider", "quality_guard", "final_answer_governance"]

    elif {"crie","gerar","estratégia","copy","marketing","conteudo","conteúdo"} & t:
        intent = "generate_strategy_or_content"
        required_outputs = ["estrategia", "plano", "resposta_final"]
        required_capabilities = ["knowledge_provider", "generation", "quality_guard", "naturalizer", "final_answer_governance"]

    elif {"automatizar","automação","sistema","pipeline","runtime"} & t:
        intent = "design_or_automate_system"
        required_outputs = ["arquitetura", "passos", "execucao", "resposta_final"]
        required_capabilities = ["planner", "knowledge_provider", "governance", "quality_guard", "final_answer_governance"]

    elif {"mercedes","aks","carro","cambio","câmbio","embreagem","entra"} & t:
        intent = "diagnose_or_validate"
        required_outputs = ["diagnostico", "causa_provavel", "proximo_passo", "resposta_final"]
        required_capabilities = ["knowledge_provider", "diagnostic", "quality_guard", "final_answer_governance"]

    elif {"prossiga","continuar","avançar"} & t:
        intent = "continue_current_mission"
        required_outputs = ["proximo_passo", "execucao", "resposta_final"]
        required_capabilities = ["memory", "planner", "quality_guard", "final_answer_governance"]

    return {
        "input": text,
        "goal": goal,
        "intent": intent,
        "required_outputs": required_outputs,
        "required_capabilities": required_capabilities,
        "tokens": sorted(t),
        "mode": "shadow_only"
    }
