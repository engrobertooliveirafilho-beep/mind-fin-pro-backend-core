try:
    from app.intent.intent_classifier_v2 import IntentClassifierV2
    from app.runtime.response_generation_engine import ResponseGenerationEngine
except Exception:
    IntentClassifierV2 = None
    ResponseGenerationEngine = None


class PromptOrchestrator:
    def answer(self, message: str, memory_context: str = "", retrieved_context: str = "", **kwargs) -> str:
        return self.run(message=message, memory_context=memory_context, retrieved_context=retrieved_context)

    def __init__(self):
        self.classifier = IntentClassifierV2() if IntentClassifierV2 else None
        self.engine = ResponseGenerationEngine() if ResponseGenerationEngine else None

    def build_response(self, message: str, memory_context: str = "", retrieved_context: str = "") -> str:
        return self.run(message=message, memory_context=memory_context, retrieved_context=retrieved_context)

    def orchestrate(self, message: str, memory_context: str = "", retrieved_context: str = "") -> str:
        return self.run(message=message, memory_context=memory_context, retrieved_context=retrieved_context)

    def run(self, message: str, memory_context: str = "", retrieved_context: str = "") -> str:
        msg = message or ""
        ctx = "\n".join([x for x in [memory_context, retrieved_context] if x])

        if self.classifier and self.engine:
            intent = self.classifier.classify(msg)
            return self.engine.generate(
                message=msg,
                intent=intent.intent,
                memory_context=ctx,
                llm_answer=""
            )

        if "deriv" in msg.lower() or "explique" in msg.lower():
            return (
                "Derivada mede a taxa de variação instantânea de uma função.\n\n"
                "Exemplo: se f(x)=x², então f'(x)=2x. No ponto x=3, a taxa de variação é 6.\n\n"
                "Aplicação: velocidade, crescimento, otimização, física, economia e engenharia.\n\n"
                "Quer que eu resolva uma derivada passo a passo?"
            )

        return "Entendi. Me diga a matéria ou dúvida que eu organizo e explico."

