from app.tutor.tutor_reasoning_layer import TutorReasoningLayer

class ResponseGenerationEngine:
    def __init__(self):
        self.tutor = TutorReasoningLayer()

    def generate(self, message: str, intent: str, memory_context: str = '', llm_answer: str = '') -> str:
        if intent == 'EDUCATIONAL_EXPLANATION':
            d = self.tutor.build_explanation(message, memory_context)
            return f"""{d['concept']}

Exemplo: {d['example']}

Passo a passo:
- {chr(10).join(d['steps'])}

AplicaÃ§Ã£o: {d['application']}

{d['check_question']}"""
        if intent == 'CONVERSATION':
            return 'Oi, Roberto. Me manda uma matÃ©ria, dÃºvida, PDF ou Ã¡udio de aula que eu organizo e explico para vocÃª.'
        if intent == 'PLANNING':
            return 'Plano de estudo: 1) mapear conteÃºdo, 2) revisar teoria, 3) fazer exercÃ­cios, 4) criar flashcards, 5) simulado curto.'
        if intent == 'MEMORY_STORE':
            return 'InformaÃ§Ã£o registrada e contexto atualizado.'
        if intent == 'MEMORY_QUERY':
            return llm_answer or 'Vou consultar sua memÃ³ria antes de responder.'
        if intent == 'SUMMARIZATION':
            return llm_answer or 'Envie o conteÃºdo que eu resumo em tÃ³picos, conceitos-chave e plano de revisÃ£o.'
        if intent in ['PDF_ANALYSIS','AUDIO_TRANSCRIPTION']:
            return 'Pode enviar o material. Eu extraio, resumo, explico e transformo em plano de estudo.'
        return llm_answer or 'Entendi. Vou seguir pelo caminho mais direto.'
