class HumanLikeResponseLayer:
    def answer(self, message, context=""):
        msg = str(message).lower()

        if msg.strip() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
            return "Oi, Roberto. Estou aqui para te ajudar com seus estudos de forma direta e organizada."

        if "como você funciona" in msg or "como voce funciona" in msg:
            return "Eu uso sua memória, seu contexto de estudo e o histórico da conversa para responder com mais precisão."

        return None
