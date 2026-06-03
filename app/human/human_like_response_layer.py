import unicodedata
from app.human.multi_llm_runtime import MultiLLMRuntime

class HumanLikeResponseLayer:

    def __init__(self):
        self.llm = MultiLLMRuntime()

    def _normalize(self, value):
        text = str(value).lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in text if not unicodedata.combining(c)])
        text = text.replace("matema¡tica", "matematica")
        text = text.replace("vocaª", "voce")
        text = text.replace("vocãª", "voce")
        text = text.replace("a©", "e")
        return text

    def build_prompt(self, message, context=""):
        return f"""
Você é a Eldora do MIND. Converse pelo WhatsApp com continuidade, memória curta e naturalidade.

Mensagem do usuário:
{message}

Contexto/memória disponível:
{context}

Responda:
- de forma humana e natural
- sem parecer FAQ
- usando contexto quando existir
- com objetividade
- em português do Brasil
"""

    def answer(self, message, context=""):
        prompt = self.build_prompt(message, context)
        llm_response = self.llm.generate(prompt)
        if llm_response:
            return llm_response
        return None
