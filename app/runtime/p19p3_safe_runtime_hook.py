from typing import Optional

def p19p3_safe_runtime_hook(user_text: str, previous_context: Optional[str] = None) -> Optional[str]:
    text = (user_text or "").strip().lower()
    context = (previous_context or "").strip().lower()

    if not text:
        return None

    if "nao entnedeu" in text or "nao entendeu" in text or "não entendeu" in text:
        return "Entendi. Vou continuar pelo contexto anterior, sem reiniciar a conversa."

    if ("desligado" in text and "ligado" in text and "marcha" in text) or "aks" in text:
        return (
            "Isso aponta mais para acionamento da embreagem/AKS do que para câmbio interno. "
            "Se desligado as marchas entram e ligado ficam duras, a embreagem provavelmente não está desacoplando totalmente. "
            "Prioridade: atuador AKS, curso da embreagem, sangria/calibração e ajuste do sistema."
        )

    if "me envia o link" in text or "manda o link" in text or "me mande o link" in text:
        if any(x in context for x in ["peça", "peca", "atuador", "embreagem", "aks", "mercedes", "classe a"]):
            return (
                "Sim. Pelo contexto, você está falando da peça, não do carro. "
                "Me mande o nome exato, código ou foto da peça que eu te ajudo a localizar o link compatível."
            )
        return "Qual item exato você quer que eu procure?"

    if any(x in text for x in ["aprofunde", "continua", "explica melhor", "qual deles"]) and context:
        return "Continuando pelo contexto anterior: vou direto ao ponto, comparando risco, causa provável e melhor decisão."

    if "compare" in text or "compara" in text:
        return "Comparação objetiva: vou organizar por vantagem, desvantagem, risco e melhor escolha."

    return None
