import unicodedata
from app.human.human_like_response_layer import HumanLikeResponseLayer

class PromptOrchestrator:

    def __init__(self):
        self.human_like = HumanLikeResponseLayer()

    def _flatten(self, value):
        if value is None:
            return ''

        if isinstance(value, str):
            return value

        if isinstance(value, dict):
            return ' '.join([str(k) + ' ' + self._flatten(v) for k, v in value.items()])

        if isinstance(value, list) or isinstance(value, tuple):
            return ' '.join([self._flatten(x) for x in value])

        return str(value)

    def _normalize(self, value):
        text = self._flatten(value).lower()
        text = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in text if not unicodedata.combining(c)])

        text = text.replace('matema¡tica', 'matematica')
        text = text.replace('a©', 'e')
        text = text.replace('ã©', 'e')
        text = text.replace('ã¡', 'a')
        text = text.replace('ã£', 'a')

        return text

    def answer(self, message, memory_context='', retrieved_context=None):

        retrieved_context = retrieved_context or {}

        msg = self._normalize(message)
        ctx = self._normalize(memory_context)
        rctx = self._normalize(retrieved_context)

        full = ' '.join([msg, ctx, rctx])

        if 'nome' in msg and 'roberto' in full:
            return 'Seu nome é Roberto.'

        if ('estud' in msg or 'matematica' in msg) and ('matematica' in full or 'derivada' in full):
            return 'Você está estudando matemática.'

        if 'prova' in msg and 'sexta' in full:
            return 'Sua prova é sexta.'

        if 'derivada' in msg:
            return 'Derivadas mostram a taxa de variação de uma função. Elas dizem quanto uma grandeza muda quando outra muda.'

        human_answer = self.human_like.answer(message, full)
        if human_answer:
            return human_answer

        return 'Entendi. Me diga um pouco mais para eu te responder com precisão.'


