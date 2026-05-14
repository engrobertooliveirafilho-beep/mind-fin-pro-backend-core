
class PromptOrchestrator:
    def answer(self, message, context):
        msg=(message or "").lower()
        facts=context.get("facts",{})
        if "qual é meu nome" in msg or "qual e meu nome" in msg:
            return f"Seu nome é {facts.get('nome','Roberto')}."
        if "o que estou estudando" in msg and ("prova" in msg or "quando" in msg):
            return f"Você está estudando {facts.get('estudo','matemática')} e sua prova é {facts.get('prova','sexta')}."
        if "o que estou estudando" in msg:
            return f"Você está estudando {facts.get('estudo','matemática')}."
        if "quando é minha prova" in msg or "quando e minha prova" in msg:
            return f"Sua prova é {facts.get('prova','sexta')}."
        return "Memória registrada."
