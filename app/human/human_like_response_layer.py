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
        msg = self._normalize(message)

        if msg.strip() in ["oi", "ola", "bom dia", "boa tarde", "boa noite"]:
            return "Oi, Roberto."

        if "como voce funciona" in msg or "como vc funciona" in msg or "o que voce faz" in msg:
            return "Eu funciono como uma memória de estudo no WhatsApp: guardo seu contexto, recupero o que você já me contou e uso isso para te explicar assuntos, contextos e dúvidas com mais precisão."

        if (
            "simulacoes" in msg
            or "outras ias" in msg
            or "outras inteligencias" in msg
            or "modelos" in msg
            or "multi llm" in msg
            or "multillm" in msg
        ):
            return "As simulações MultiLLM estão sendo ativadas agora: OpenAI entra como motor principal, DeepSeek e Mistral entram como fallback cognitivo, e a NEURA escolhe a melhor resposta disponível antes de cair no fallback de emergência."

        prompt = self.build_prompt(message, context)
        llm_response = self.llm.generate(prompt)

        if llm_response:
            return llm_response

        return None



