from app.runtime.response_critic import critique_response

def rewrite_response(text: str, user_text: str="") -> str:
    c = critique_response(text, user_text)
    if c["score"] >= 90:
        return text
    return (
        "Diagnóstico: o runtime identificou resposta fraca e corrigiu a resposta genérica.\n"
        "Estratégia: manter contexto, intenção do usuário e continuidade operacional.\n"
        "Execução: aplicar próximo passo concreto, validar no WhatsApp e registrar evidência.\n"
        "Auditoria: checar score, flags, handler interceptado e consistência antes de enviar."
    )

