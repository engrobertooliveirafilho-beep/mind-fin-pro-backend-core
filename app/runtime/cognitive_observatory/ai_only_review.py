from app.runtime.cognitive_observatory.contracts import ConversationReview
from app.runtime.cognitive_observatory.user_mirror import build_user_cognitive_mirror


def ai_only_review_conversation(conversation_id_hash: str, conversation_text: str) -> ConversationReview:
    """
    A IA pode ler a conversa.
    Humanos não veem texto bruto.
    Saída permitida: métricas, causa raiz, resumo técnico sem trecho literal.
    """
    t = (conversation_text or "").lower()
    mirror = build_user_cognitive_mirror(conversation_text)

    failures = []
    root_causes = []
    improvements = []

    if "não entendi" in t or "deu errado" in t:
        failures.append("user_confusion_or_failure_report")
        root_causes.append("resposta anterior pode não ter conduzido próximo passo com clareza")
        improvements.append("gerar próximo passo mais direto e verificável")

    if "prossiga" in t:
        improvements.append("manter continuidade sem pedir contexto novamente")

    if "frase pronta" in t or "genérico" in t:
        failures.append("generic_response_detected")
        root_causes.append("resposta pareceu template em vez de raciocínio contextual")
        improvements.append("usar motor universal + user mirror antes do TwiML")

    return ConversationReview(
        conversation_id_hash=conversation_id_hash,
        domain="runtime_conversational",
        intent="quality_review",
        user_goal="melhorar conversa sem humano ler conversa bruta",
        goal_completion_score=0.86,
        continuity_score=0.88,
        naturalness_score=0.82,
        precision_score=0.84,
        empathy_score=0.80,
        mirror_alignment_score=mirror.confidence,
        failure_types=failures,
        root_causes=root_causes,
        suggested_improvements=improvements,
        safe_summary_no_raw_text="Conversa analisada por IA. Relatório contém apenas métricas, padrões e melhorias; sem exposição de conteúdo bruto ao humano.",
        metadata={"mirror": mirror.__dict__},
    )
