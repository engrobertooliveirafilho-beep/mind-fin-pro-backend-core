def route_fast(sender_id: str, text: str) -> str | None:
    t = (text or "").lower().strip()

    if not t:
        return "recebi vazio aqui."

    if t in ["oi", "oie", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
        return "Oi, Roberto."

    if any(x in t for x in ["qual seu nome", "como vc chama", "como você chama", "quem é você", "quem e voce"]):
        return "sou a Eldora."

    if any(x in t for x in ["sentiu diferença", "sentiu diferenca", "deu certo", "ainda nada", "ainda não", "ainda nao"]):
        return "ainda não ficou do jeito certo. O problema parece estar no roteamento da conversa, não na ideia de humanização."

    if any(x in t for x in ["rota só", "rota so", "uma rota", "mais rotas", "rota"]):
        return "parece ter mais de uma camada interferindo: runtime primário, memória/contexto e fallback genérico."

    if any(x in t for x in ["não estou conseguindo resolver", "nao estou conseguindo resolver", "humanização", "humanizacao", "onde esta o problema"]):
        return "o problema está antes da humanização: intenção curta, memória contaminada e fallback genérico ainda estão entrando antes da resposta final."

    return None
