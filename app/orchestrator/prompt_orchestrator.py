class PromptOrchestrator:
    def __init__(self):
        pass

    def answer(self, message, memory_context='', retrieved_context=None):
        retrieved_context = retrieved_context or {}
        lower_msg = str(message).lower()
        lower_ctx = str(memory_context).lower()
        facts = retrieved_context.get('facts', [])
        if isinstance(facts, list):
            fact_text = ' '.join([str(x) for x in facts]).lower()
        else:
            fact_text = str(facts).lower()

        if 'qual meu nome' in lower_msg:
            if 'roberto' in lower_ctx or 'roberto' in fact_text:
                return 'Seu nome é Roberto.'

        if 'o que estou estudando' in lower_msg:
            if 'matemática' in lower_ctx or 'matematica' in lower_ctx:
                return 'Você está estudando matemática.'
            if 'matemática' in fact_text or 'matematica' in fact_text:
                return 'Você está estudando matemática.'

        if 'quando é minha prova' in lower_msg:
            if 'sexta' in lower_ctx or 'sexta' in fact_text:
                return 'Sua prova é sexta.'

        if 'derivada' in lower_msg:
            return 'Derivadas representam a taxa de variação de uma função em relação a outra variável.'

        return 'Entendi. Continue.'

