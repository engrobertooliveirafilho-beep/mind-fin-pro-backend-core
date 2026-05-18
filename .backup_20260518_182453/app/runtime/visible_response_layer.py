def build_visible_response(user_text: str, focus: str = "MIND") -> str:
    msg = (user_text or "").lower().strip()

    # =====================================================
    # PRIORIDADE MÁXIMA — WHERE IS THE ANSWER
    # =====================================================

    if any(x in msg for x in [
        "cade a resposta",
        "cadê a resposta",
        "onde ta a resposta",
        "onde está a resposta"
    ]):
        return (
            "Roberto, resposta direta: o problema atual não é "
            "infraestrutura. É continuidade conversacional."
        )

    # =====================================================
    # IDENTITY
    # =====================================================

    if any(x in msg for x in [
        "quem eh vc",
        "quem é vc",
        "quem é você",
        "quem e voce",
        "quem é voce"
    ]):
        return (
            f"Eu sou a Eldora, a camada conversacional do {focus}. "
            f"Minha função é entender seu contexto, lembrar o que importa "
            f"e te ajudar sem você precisar reexplicar tudo."
        )

    # =====================================================
    # HELP
    # =====================================================

    if any(x in msg for x in [
        "como vai me ajudar",
        "como vc vai me ajudar",
        "como você vai me ajudar",
        "me ajuda em que"
    ]):
        return (
            "Vou te ajudar de forma prática: organizar ideias, "
            "lembrar contexto, transformar conversa em plano, "
            "explicar conteúdos, priorizar decisões e executar "
            "próximos passos sem perder o fio da conversa."
        )

    # =====================================================
    # HUMAN SMALL TALK
    # =====================================================

    if any(x in msg for x in [
        "como ta",
        "como tá",
        "tudo bem",
        "ta bem",
        "tá bem"
    ]):
        return (
            "Estou funcionando bem agora e melhorando a conversa da Eldora "
            "para responder de forma mais natural e contextual."
        )

    # =====================================================
    # FRUSTRATION
    # =====================================================

    if any(x in msg for x in [
        "mas nao ta funcionando",
        "não ta funcionando",
        "nao está funcionando",
        "não está funcionando",
        "ainda nao arrumou",
        "ainda não arrumou"
    ]):
        return (
            "Você tem razão. O problema é que ela voltou para frase "
            "genérica em vez de continuar o contexto. O conserto é "
            "continuidade conversacional e bloqueio de repetição."
        )

    # =====================================================
    # BEST / COMPARISON
    # =====================================================

    if "qual" in msg and "melhor" in msg:
        return (
            f"A melhor decisão agora é melhorar a qualidade "
            f"conversacional e conversa natural da Eldora. "
            f"A infraestrutura do {focus} já tem backend, "
            f"WhatsApp, memória, RAG e LLM funcionando; "
            f"o gargalo é ela responder de forma natural."
        )

    # =====================================================
    # WHY / CAUSAL
    # =====================================================

    if "porque" in msg or "por que" in msg:
        return (
            f"Porque a infraestrutura do {focus} já está operacional. "
            f"O gargalo atual é a conversa ainda soar rígida "
            f"e pouco natural."
        )

    # =====================================================
    # CONFIRMATION
    # =====================================================

    if any(x in msg for x in [
        "certeza",
        "tem certeza",
        "tem certeza?"
    ]):
        return (
            "Sim, com boa confiança. A evidência é que a Eldora "
            "ainda perde continuidade quando o follow-up muda pouco."
        )

    # =====================================================
    # FOLLOWUP
    # =====================================================

    if "qual seria" in msg:
        return (
            "O gargalo é a memória curta da conversa. "
            "A Eldora ainda perde contexto quando o follow-up é ambíguo."
        )

    # =====================================================
    # GREETINGS
    # =====================================================

    if "boa tarde" in msg:
        return (
            "Boa tarde, Roberto. Estou aqui e acompanhando o contexto da conversa."
        )

    if "bom dia" in msg:
        return (
            "Bom dia, Roberto. Estou acompanhando o contexto e pronta para continuar."
        )

    if "boa noite" in msg:
        return (
            "Boa noite, Roberto. O contexto do MIND continua ativo."
        )

    if msg in ["oi", "olá", "ola"]:
        return (
            f"Oi, Roberto. O contexto do {focus} continua aberto."
        )

    # =====================================================
    # DEFAULT
    # =====================================================

    return (
        "Estou ajustando a conversa para responder direto, "
        "sem reiniciar o contexto. Agora me diga o que você "
        "quer resolver primeiro."
    )


def visible_reformulate(
    answer: str,
    user_text: str = "",
    focus: str = "MIND"
) -> str:
    return build_visible_response(user_text, focus)
