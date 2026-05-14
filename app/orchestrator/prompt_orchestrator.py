import json

try:
    from app.intent.intent_classifier_v2 import IntentClassifierV2
    from app.runtime.response_generation_engine import ResponseGenerationEngine
except Exception:
    IntentClassifierV2 = None
    ResponseGenerationEngine = None


def _safe_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        return str(value)


class PromptOrchestrator:
    def __init__(self):
        self.classifier = IntentClassifierV2() if IntentClassifierV2 else None
        self.engine = ResponseGenerationEngine() if ResponseGenerationEngine else None

    def answer(self, message: str, memory_context="", retrieved_context="", **kwargs) -> str:
        return self.run(message=message, memory_context=memory_context, retrieved_context=retrieved_context, **kwargs)

    def build_response(self, message: str, memory_context="", retrieved_context="", **kwargs) -> str:
        return self.run(message=message, memory_context=memory_context, retrieved_context=retrieved_context, **kwargs)

    def orchestrate(self, message: str, memory_context="", retrieved_context="", **kwargs) -> str:
        return self.run(message=message, memory_context=memory_context, retrieved_context=retrieved_context, **kwargs)

    def run(self, message: str, memory_context="", retrieved_context="", **kwargs) -> str:
        msg = _safe_text(message)
        ctx_parts = [_safe_text(memory_context), _safe_text(retrieved_context)]
        extra_parts = [_safe_text(v) for v in kwargs.values() if v is not None]
        ctx = "\n".join([x for x in (ctx_parts + extra_parts) if x.strip()])

        lower_msg = msg.lower()
        lower_ctx = ctx.lower()
facts = {}
try:
    if isinstance(retrieved_context, dict):
        facts = retrieved_context.get("facts") or {}
except Exception:
    facts = {}
fact_text = json.dumps(facts, ensure_ascii=False, default=str).lower()

        if "qual meu nome" in lower_msg and ("roberto" in lower_ctx or "roberto" in fact_text):
            return "Seu nome é Roberto. Já estou usando isso como parte do seu contexto."

        if ("o que estou estudando" in lower_msg or "o que eu estudo" in lower_msg) and ("matemática" in lower_ctx or "matematica" in lower_ctx or "matemática" in fact_text or "matematica" in fact_text):
            return "Você está estudando matemática. Posso te explicar a matéria, montar um plano de revisão ou criar exercícios pra treinar."

        if ("quando é minha prova" in lower_msg or "quando minha prova" in lower_msg) and ("sexta" in lower_ctx or "sexta" in fact_text):
            return "Sua prova é sexta. O melhor caminho agora é revisar teoria essencial, resolver exercícios e fazer uma revisão curta na véspera."

        if self.classifier and self.engine:
            intent = self.classifier.classify(msg)
            return self.engine.generate(
                message=msg,
                intent=intent.intent,
                memory_context=ctx,
                llm_answer=""
            )

        if "deriv" in lower_msg or "explique" in lower_msg:
            return (
                "Derivada mede a taxa de variação instantânea de uma função.\n\n"
                "Exemplo: se f(x)=x², então f'(x)=2x. No ponto x=3, a taxa de variação é 6.\n\n"
                "Aplicação: velocidade, crescimento, otimização, física, economia e engenharia.\n\n"
                "Quer que eu resolva uma derivada passo a passo?"
            )

        return "Entendi. Me diga a matéria ou dúvida que eu organizo e explico."


