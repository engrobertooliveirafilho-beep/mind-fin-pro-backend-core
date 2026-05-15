import unicodedata

class HumanLikeResponseLayer:

    def _normalize(self, value):
        text = str(value).lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in text if not unicodedata.combining(c)])
        text = text.replace("matema¡tica", "matematica")
        text = text.replace("vocaª", "voce")
        text = text.replace("vocãª", "voce")
        return text

    def build_prompt(self, message, context=""):
        return f"""
Você é a NEURA, uma tutora cognitiva para estudantes via WhatsApp.
Responda de forma humana, direta, útil e contextual.

Mensagem do aluno:
{message}

Contexto disponível:
{context}

Regras:
- Não diga que é apenas um sistema.
- Use memória quando existir.
- Explique com clareza.
- Seja natural, mas objetivo.
"""

    def answer(self, message, context="", llm=None):
        msg = self._normalize(message)

        if llm:
            try:
                response = llm.generate(self.build_prompt(message, context))
                if response and len(str(response).strip()) > 5:
                    return str(response).strip()
            except Exception:
                pass

        if msg.strip() in ["oi", "ola", "bom dia", "boa tarde", "boa noite"]:
            return "Oi, Roberto. Estou aqui para te ajudar com seus estudos de forma direta e organizada."

        if "como voce funciona" in msg or "como vc funciona" in msg or "o que voce faz" in msg:
            return "Eu funciono como uma memória de estudo no WhatsApp: guardo seu contexto, recupero o que você já me contou e uso isso para te explicar matérias, provas e dúvidas com mais precisão."

        return None
