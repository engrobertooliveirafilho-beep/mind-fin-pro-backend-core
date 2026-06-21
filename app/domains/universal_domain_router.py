from __future__ import annotations

def generic_contextual_reply(text: str, ctx: dict) -> str:
    domain = ctx.get("active_domain", "assunto")
    subject = ctx.get("active_subject", "o ponto anterior")

    return (
        f"Vou continuar no mesmo contexto: {subject}. "
        f"O próximo passo é aprofundar esse assunto sem trocar de tema. "
        f"Me diga se você quer checklist, plano prático ou explicação detalhada."
    )

def route_domain_reply(text: str, ctx: dict):
    domain = ctx.get("active_domain")

    if domain == "fitness":
        try:
            from app.domains.fitness_runtime import reply
            return reply(text)
        except Exception:
            return generic_contextual_reply(text, ctx)

    if domain == "agro":
        return (
            "Continuando no agro: primeiro defina objetivo, estrutura disponível, custo por animal, alimentação, água, manejo e controle diário. "
            "Depois eu monto o plano operacional por etapa."
        )

    if domain == "trader":
        return (
            "Continuando no trader: primeiro validamos hipótese, ativo, timeframe, regra de entrada, stop, alvo, risco e backtest. "
            "Sem isso, nada vai para execução."
        )

    if domain == "eldora_launch":
        return (
            "Continuando o lançamento da Eldora: agora é oferta, público, canal, CTA, prova de valor e simulação de risco antes de escalar tráfego."
        )

    return generic_contextual_reply(text, ctx)
