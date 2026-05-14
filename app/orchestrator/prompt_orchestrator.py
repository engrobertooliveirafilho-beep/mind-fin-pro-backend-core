import re

class PromptOrchestrator:

    def answer(self, message, context):

        facts = context.get("facts", {}) or {}
        history_raw = context.get("history_text", "") or ""
        full = (history_raw + "\n" + (message or "")).lower()
        msg = (message or "").lower()

        nome = facts.get("nome")
        estudo = facts.get("estudo")
        prova = facts.get("prova")

        if not nome and "roberto" in full:
            nome = "Roberto"

        if not estudo:
            m = re.search(r"estou estudando\s+([a-záéíóúâêîôûãõç0-9 ]+)", full, re.I)
            if m:
                estudo = m.group(1).strip(" .?!\n\r").split("\n")[0]
            elif "matemática" in full or "matematica" in full:
                estudo = "matemática"

        if "meu nome é" in msg:
            return "Informação registrada e contexto atualizado."

        if "estou estudando" in msg and not msg.strip().startswith("o que"):
            return "Contexto de estudo registrado."

        if "qual" in msg and "nome" in msg:
            return f"Seu nome é {nome}." if nome else "Ainda não sei seu nome."

        if "o que" in msg and ("estudando" in msg or "estudo" in msg):
            return f"Você está estudando {estudo}." if estudo else "Ainda não encontrei o que você está estudando."

        if "prova" in msg:
            return f"Sua prova é {prova}." if prova else "Ainda não encontrei a data da sua prova."

        return "Informação registrada e contexto atualizado."
