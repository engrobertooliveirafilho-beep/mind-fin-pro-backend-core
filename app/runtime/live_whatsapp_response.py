from app.runtime.whatsapp_trace_sensor import sanitize_final_output
from app.dialogue.conversation_continuity_runtime import update,get
from app.dialogue.context_resolution_engine import resolve
from app.dialogue.generic_llm_detector import detect,rewrite
from app.dialogue.persona_consistency_guard import enforce
from app.humanization.universal_recovery_runtime import semantic_recovery
from app.runtime.identity_guard_runtime import guard_identity_fallback
def live_whatsapp_response(message: str) -> str | None:
    msg = (message or "").lower().strip()

    if msg in ["i", "oi", "olá", "ola"]:
        return "Oi, Roberto. Estou aqui. Vamos resolver isso direto."

    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda não conseguimos resolver", "nao esta funcionando", "não está funcionando", "não funciona"]):
        return "Ainda não ficou bom no WhatsApp real. O próximo passo é corrigir o handler do canal, não criar mais camada."

    if any(x in msg for x in ["o que fazer", "oque fazer", "como resolver", "como arrumar"]):
        return "Agora é simples: colocar uma resposta viva antes do pipeline cognitivo, testar no WhatsApp e só depois religar a cognição completa."

    if any(x in msg for x in ["como ta", "como tá", "tudo bem", "boa tarde", "bom dia", "boa noite"]):
        return "Estou funcionando, mas o WhatsApp ainda precisa desse ajuste de resposta viva para não cair em frase genérica."

    if any(x in msg for x in ["quem eh vc", "quem é vc", "quem é você"]):
        return semantic_recovery(msg if "msg" in locals() else user_text if "user_text" in locals() else inbound_text if "inbound_text" in locals() else "")

    return None



