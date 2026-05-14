
class PromptOrchestrator:

    def answer(self, message, context):

        facts = context.get("facts", {})
        history = context.get("history_text", "")

        msg = (message or "").lower()

        # =========================
        # NOME
        # =========================
        if "qual é meu nome" in msg or "meu nome" in msg:
            nome = facts.get("nome")
            if nome:
                return f"Seu nome é {nome}."
            return "Ainda não sei seu nome."

        # =========================
        # ESTUDO
        # =========================
        if "o que estou estudando" in msg:
            estudo = facts.get("estudo")
            if estudo:
                return f"Você está estudando {estudo}."
            return "Ainda não encontrei o que você está estudando."

        # =========================
        # PROVA
        # =========================
        if "quando é minha prova" in msg:
            prova = facts.get("prova")
            if prova:
                return f"Sua prova é {prova}."
            return "Ainda não encontrei a data da sua prova."

        # =========================
        # CONTEXTO GERAL
        # =========================
        if "resuma meu contexto" in msg:
            if history:
                return f"Resumo do seu contexto: {history[:500]}"
            return "Ainda não tenho contexto suficiente."

        # =========================
        # MEMÓRIA PADRÃO
        # =========================
        return "Informação registrada e contexto atualizado."

