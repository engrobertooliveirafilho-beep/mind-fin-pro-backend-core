def route_fast(sender_id: str, text: str) -> str | None:
    t = (text or "").lower().strip()

    greetings = [
        "oi","oie","olá","ola",
        "bom dia","boa tarde","boa noite"
    ]

    if not t:
        return "te ouvi aqui, mas veio vazio."

    if t in greetings:
        return "Oi, Roberto."

    if any(x in t for x in [
        "tudo bem","tudo certo","como ta","como tá",
        "como vc ta","como você está","e vc","e você"
    ]):
        return "Tudo certo por aqui 🙂 E você?"

    if any(x in t for x in [
        "qual seu nome","como vc chama",
        "como você chama","quem é você",
        "quem e voce"
    ]):
        return "Sou a Eldora 🙂"

    if any(x in t for x in [
        "sentiu diferença","sentiu diferenca",
        "deu certo","ou ainda nada",
        "ainda nada","ainda não","ainda nao"
    ]):
        return "melhorou um pouco, mas ainda tem problema de continuidade e respostas genéricas."

    if any(x in t for x in [
        "verificar onde esta o problema",
        "onde esta o problema",
        "consegue verificar",
        "procura por ai",
        "procura por aí"
    ]):
        return "consigo. O principal problema parece estar no roteamento: intenção curta, fallback genérico e memória contaminada."

    if any(x in t for x in [
        "rota só","rota so","uma rota",
        "mais rotas","é uma rota","rota"
    ]):
        return "parece mais de uma camada interferindo: runtime principal, memória/contexto e fallback."

    return None
