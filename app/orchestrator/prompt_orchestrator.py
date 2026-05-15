import unicodedata

class PromptOrchestrator:
    def __init__(self):
        print('PROMPT_ORCHESTRATOR_INIT_OK')

    def _normalize(self, text):
        text = str(text).lower()
        text = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in text if not unicodedata.combining(c)])

    def answer(self, message, memory_context='', retrieved_context=None):

        print('ANSWER_METHOD_CALLED')
        print(f'MESSAGE_RAW={message}')
        print(f'MEMORY_CONTEXT={memory_context}')
        print(f'RETRIEVED_CONTEXT={retrieved_context}')

        msg = self._normalize(message)

        print(f'MESSAGE_NORMALIZED={msg}')

        if 'matematica' in msg:
            print('MATCH_MATEMATICA_OK')
            return 'Você está estudando matemática.'

        if 'sexta' in msg:
            print('MATCH_SEXTA_OK')
            return 'Sua prova é sexta.'

        return 'FALLBACK_TRIGGERED'


