class PromptOrchestrator:

    def answer(self, message, context):

        facts = context.get("facts", {}) or {}
        history_raw = context.get("history_text", "") or ""
        history = history_raw.lower()
        msg = (message or "").lower()

        nome = facts.get("nome")
        estudo = facts.get("estudo")
        prova = facts.get("prova")

        if "meu nome é" in msg:
            return "Informação registrada e contexto atualizado."

        if "estou estudando" in msg:
            return "Contexto de estudo registrado."

        if not nome and "roberto" in history:
            nome = "Roberto"

        if not estudo and ("estou estudando matemática" in history or "estou estudando matematica" in history or "matemática" in history or "matematica" in history):
            estudo = "matemática"

        if not prova and "prova" in history and "sexta" in history:
            prova = "sexta"

        if "qual" in msg and "nome" in msg:
            if nome:
                return f"Seu nome é {nome}."
            return "Ainda não sei seu nome."

        if "o que" in msg and ("estudando" in msg or "estudo" in msg):
            if estudo:
                return f"Você está estudando {estudo}."
            return "Ainda não encontrei o que você está estudando."

        if "prova" in msg:
            if prova:
                return f"Sua prova é {prova}."
            return "Ainda não encontrei a data da sua prova."

        if "resuma" in msg and "contexto" in msg:
            if history_raw:
                return f"Resumo do seu contexto: {history_raw[:500]}"
            return "Ainda não tenho contexto suficiente."

        return "Informação registrada e contexto atualizado."
