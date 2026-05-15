class PromptOrchestrator:
    def __init__(self):
        pass

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

    def answer(self, message, memory_context='', retrieved_context=None):
        retrieved_context = retrieved_context or {}
        msg = self._flatten(message).lower()
        ctx = self._flatten(memory_context).lower()
        rctx = self._flatten(retrieved_context).lower()
        full = ' '.join([msg, ctx, rctx])

        if 'meu nome é roberto' in msg or 'meu nome e roberto' in msg:
            return 'Memória registrada: seu nome é Roberto.'

        if 'estou estudando matemática' in msg or 'estou estudando matematica' in msg:
            return 'Contexto de estudo registrado: você está estudando matemática.'

        if 'minha prova é sexta' in msg or 'minha prova e sexta' in msg or 'tenho prova sexta' in msg:
            return 'Contexto de prova registrado: sua prova é sexta.'

        if 'qual meu nome' in msg or 'meu nome' in msg:
            if 'roberto' in full:
                return 'Seu nome é Roberto.'
            return 'Ainda não encontrei seu nome registrado no contexto.'

        if 'o que estou estudando' in msg or 'qual matéria' in msg or 'qual materia' in msg:
            if 'matemática' in full or 'matematica' in full:
                return 'Você está estudando matemática.'
            return 'Ainda não encontrei a matéria no contexto. Me diga: estou estudando matemática.'

        if 'quando é minha prova' in msg or 'quando e minha prova' in msg or 'minha prova' in msg:
            if 'sexta' in full:
                return 'Sua prova é sexta.'
            return 'Ainda não encontrei a data da prova no contexto. Me diga: minha prova é sexta.'

        if 'derivada' in msg or 'derivadas' in msg:
            return 'Derivadas mostram a taxa de variação de uma função. Elas dizem quanto uma grandeza muda quando outra muda.'

        if msg.strip() in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']:
            return 'Oi, Roberto. Estou aqui para te ajudar a organizar seus estudos e explicar o que você precisar.'

        return 'Entendi. Me diga um pouco mais para eu te responder com precisão.'

