import unicodedata

class HumanLikeResponseLayer:

    def _normalize(self, value):
        text = str(value).lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in text if not unicodedata.combining(c)])
        text = text.replace("voce", "voce")
        text = text.replace("vocaª", "voce")
        text = text.replace("vocãª", "voce")
        return text

    def answer(self, message, context=""):
        msg = self._normalize(message)

        if msg.strip() in ["oi", "ola", "bom dia", "boa tarde", "boa noite"]:
            return "Oi, Roberto. Estou aqui para te ajudar com seus estudos de forma direta e organizada."

        if "como voce funciona" in msg or "como vc funciona" in msg or "o que voce faz" in msg:
            return "Eu funciono como uma memória de estudo no WhatsApp: guardo seu contexto, recupero o que você já me contou e uso isso para te explicar matérias, provas e dúvidas com mais precisão."

        return None
