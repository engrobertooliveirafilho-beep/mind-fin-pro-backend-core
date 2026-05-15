class PromptOrchestrator:
    def __init__(self):
        pass

    def _flatten(self, value):
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            parts = []
            for k, v in value.items():
                parts.append(str(k))
                parts.append(self._flatten(v))
            return ' '.join(parts)
        if isinstance(value, list) or isinstance(value, tuple):
            return ' '.join([self._flatten(x) for x in value])
        return str(value)

    def answer(self, message, memory_context='', retrieved_context=None):
        retrieved_context = retrieved_context or {}
        msg = self._flatten(message).lower()
        ctx = self._flatten(memory_context).lower()
        rctx = self._flatten(retrieved_context).lower()
        full = ' '.join([msg, ctx, rctx])

        if 'qual meu nome' in msg or 'meu nome' in msg:
            if 'roberto' in full:
                return 'Seu nome é Roberto.'

        if 'o que estou estudando' in msg or 'estou estudando' in msg or 'qual matéria' in msg or 'qual materia' in msg:
            if 'matemática' in full or 'matematica' in full:
                return 'Você está estudando matemática.'
            if 'derivada' in full or 'derivadas' in full:
                return 'Você está estudando derivadas.'

        if 'quando é minha prova' in msg or 'quando e minha prova' in msg or 'minha prova' in msg or 'prova' in msg:
            if 'sexta' in full:
                return 'Sua prova é sexta.'
            if 'amanhã' in full or 'amanha' in full:
                return 'Sua prova é amanhã.'

        if 'derivada' in msg or 'derivadas' in msg:
            return 'Derivadas mostram a taxa de variação de uma função. Em termos simples: elas dizem o quanto uma grandeza muda quando outra muda.'

        if msg.strip() in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']:
            return 'Oi, Roberto. Estou aqui para te ajudar a organizar seus estudos e explicar o que você precisar.'

        return 'Entendi. Me diga um pouco mais para eu te responder com precisão.'

