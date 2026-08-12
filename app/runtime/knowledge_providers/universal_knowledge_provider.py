from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class UniversalKnowledgeResult:
    provider: str
    confidence: float
    intent: str
    goal: str
    facts: List[str]
    steps: List[str]
    warnings: List[str]
    source: str = "universal_knowledge_provider"


def provide_universal_knowledge(text: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}
    low = str(text or "").lower()

    intent = "assist"
    goal = "resolver_solicitacao_do_usuario"
    facts = []
    steps = []
    warnings = []

    if any(k in low for k in ["ftmo", "trader", "trade", "backtest", "paper"]):
        intent = "diagnose_or_validate"
        facts.append("Consulta relacionada a trading deve permanecer em modo PAPER_ONLY/SHADOW até validação.")
        steps += ["diagnosticar objetivo", "validar regras e restrições", "responder sem executar ordem real"]
        warnings.append("Execução financeira real proibida neste fluxo.")

    elif any(k in low for k in ["mercedes", "aks", "câmbio", "cambio", "embreagem", "ré"]):
        intent = "diagnose_or_validate"
        facts.append("Consulta automotiva deve gerar diagnóstico orientativo, não execução física.")
        steps += ["identificar sintomas", "listar causas prováveis", "orientar verificação segura"]
        warnings.append("Não substituir mecânico qualificado.")

    elif any(k in low for k in ["boi", "gado", "confinamento", "agro", "fazenda"]):
        intent = "design_or_automate_system"
        facts.append("Consulta agro deve gerar arquitetura, passos e pontos de controle.")
        steps += ["mapear processo", "definir sensores/dados", "criar automação", "validar operação humana"]
        warnings.append("Automação operacional exige validação humana.")

    elif any(k in low for k in ["marketing", "estratégia", "copy", "criativo", "eldora"]):
        intent = "generate_strategy_or_content"
        facts.append("Consulta de marketing deve gerar plano aplicável e resposta final curta.")
        steps += ["definir oferta", "definir público", "criar ângulo", "validar CTA"]
    else:
        facts.append("Consulta geral recebida sem provider especializado.")
        steps += ["interpretar objetivo", "gerar resposta útil", "validar clareza"]

    result = UniversalKnowledgeResult(
        provider="universal_knowledge_provider",
        confidence=0.72,
        intent=intent,
        goal=goal,
        facts=facts,
        steps=steps,
        warnings=warnings,
    )

    return asdict(result)
