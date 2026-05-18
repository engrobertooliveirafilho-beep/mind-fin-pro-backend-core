def visible_reformulate(answer: str, message: str, focus: str = "MIND") -> str:
    t = (message or "").lower().strip()

    if "cad" in t and "resposta" in t:
        return "Você tem razão. A resposta direta é: o melhor agora é corrigir a conversa da Eldora para responder sua pergunta, não comentar o próprio sistema."

    if "qual" in t and "melhor" in t:
        return f"A melhor decisão agora é melhorar a qualidade conversacional e conversa natural da Eldora. O {focus} já tem backend, WhatsApp, memória, RAG e LLM funcionando; o gargalo é ela responder de forma natural."

    if "porque" in t or "por que" in t or t == "pq?":
        return f"Porque a infraestrutura do {focus} já está operacional. O gargalo atual é a conversa ainda soar rígida e pouco natural. Se continuarmos criando camada antes de corrigir a conversa, a Eldora fica maior, mas não necessariamente mais inteligente para o usuário."

    if "certeza" in t:
        return "Sim, com boa confiança. A evidência é que ela responde, mas ainda cai em repetição e metacomentário. Então o próximo gargalo é diálogo, não infraestrutura."

    if answer.startswith("Vou responder diferente"):
        return f"O ponto direto é: precisamos melhorar a conversa externa da Eldora sem mexer no núcleo operacional do {focus}."

    return answer


