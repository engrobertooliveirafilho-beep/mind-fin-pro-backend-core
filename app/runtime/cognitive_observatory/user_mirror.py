from app.runtime.cognitive_observatory.contracts import UserCognitiveMirror


def build_user_cognitive_mirror(conversation_text: str) -> UserCognitiveMirror:
    t = (conversation_text or "").lower()

    mirror = UserCognitiveMirror()

    if any(x in t for x in ["prossiga", "direto", "sem enrolar", "objetivo", "powershell"]):
        mirror.tone = "direto, operacional, sem floreio"
        mirror.detail_level = "alto quando técnico, curto na explicação"
        mirror.decision_style = "execução por missão com evidência"
        mirror.reasoning_pattern = "diagnóstico -> estratégia -> execução -> auditoria"
        mirror.vocabulary.extend(["missão", "evidência", "runtime", "auditoria", "patch", "snapshot"])

    if any(x in t for x in ["lançamento", "vender", "marketing", "criativo", "conversão"]):
        mirror.priorities.extend(["lançamento", "conversão", "retenção", "clareza de oferta"])

    if any(x in t for x in ["eldora", "mind", "whatsapp"]):
        mirror.recurring_goals.extend(["Eldora humana", "continuidade no WhatsApp", "motor universal"])

    if any(x in t for x in ["frase pronta", "genérico", "template", "robô"]):
        mirror.dislikes.extend(["frase pronta", "fallback genérico", "resposta com cara de manual"])

    mirror.confidence = 0.82
    return mirror


def apply_user_mirror_to_instruction(base_instruction: str, mirror: UserCognitiveMirror) -> str:
    return f"""
Responda como uma versão mais clara, estratégica e inteligente do usuário.

Estilo:
- Tom: {mirror.tone}
- Nível de detalhe: {mirror.detail_level}
- Decisão: {mirror.decision_style}
- Raciocínio: {mirror.reasoning_pattern}

Prioridades do usuário:
{", ".join(mirror.priorities) or "não identificado"}

Objetivos recorrentes:
{", ".join(mirror.recurring_goals) or "não identificado"}

Evitar:
{", ".join(mirror.dislikes) or "respostas genéricas"}

Instrução base:
{base_instruction}
""".strip()
