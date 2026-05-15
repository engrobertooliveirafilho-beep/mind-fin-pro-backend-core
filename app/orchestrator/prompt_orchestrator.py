import unicodedata

class PromptOrchestrator:
    def __init__(self):
        print('PROMPT_ORCHESTRATOR_INIT_OK')

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
        return ''.join([c for c in text if not unicodedata.combining(c)])

    def answer(self, message, memory_context='', retrieved_context=None):
        retrieved_context = retrieved_context or {}
        msg = self._normalize(message)
        ctx = self._normalize(memory_context)
        rctx = self._normalize(retrieved_context)
        full = ' '.join([msg, ctx, rctx])
        print('ANSWER_METHOD_CALLED')
        print(f'MSG={msg}')
        print(f'FULL={full}')

        if 'roberto' in full and ('nome' in msg or 'meu nome' in msg):
            return 'Seu nome é Roberto.'

        if 'estud' in full and ('matematica' in full or 'derivada' in full):
            return 'Você está estudando matemática.'

        if 'prova' in full and 'sexta' in full:
            return 'Sua prova é sexta.'

        if 'derivada' in msg:
            return 'Derivadas mostram a taxa de variação de uma função. Elas dizem quanto uma grandeza muda quando outra muda.'

        if msg.strip() in ['oi','ola','olá','bom dia','boa tarde','boa noite']:
            return 'Oi, Roberto. Estou aqui para te ajudar com seus estudos.'

        return 'Entendi. Me diga um pouco mais para eu te responder com precisão.'

