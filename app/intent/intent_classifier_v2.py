from dataclasses import dataclass
from enum import Enum
import re, unicodedata

class Intent(str, Enum):
    MEMORY_STORE='MEMORY_STORE'
    MEMORY_QUERY='MEMORY_QUERY'
    EDUCATIONAL_EXPLANATION='EDUCATIONAL_EXPLANATION'
    CONVERSATION='CONVERSATION'
    PLANNING='PLANNING'
    SUMMARIZATION='SUMMARIZATION'
    TASK_EXECUTION='TASK_EXECUTION'
    RESEARCH='RESEARCH'
    AUDIO_TRANSCRIPTION='AUDIO_TRANSCRIPTION'
    PDF_ANALYSIS='PDF_ANALYSIS'

@dataclass
class IntentResult:
    intent: str
    confidence: float
    reason: str

class IntentClassifierV2:
    def _norm(self, text: str) -> str:
        text = unicodedata.normalize('NFKD', text or '')
        return ''.join(c for c in text if not unicodedata.combining(c)).lower().strip()

    def classify(self, text: str) -> IntentResult:
        t = self._norm(text)
        if re.search(r'\b(qual|quem|quando|onde|lembra).*(meu|minha|nome|prova|estudo|disciplina|objetivo)\b', t):
            return IntentResult(Intent.MEMORY_QUERY.value, .94, 'memory_query')
        if re.search(r'\b(me chamo|meu nome e|estou estudando|tenho prova|minha dificuldade|meu objetivo)\b', t):
            return IntentResult(Intent.MEMORY_STORE.value, .92, 'memory_store')
        if re.search(r'\b(me explique|explique|ensine|como funciona|o que e|defina|exemplo|passo a passo|derivada|integral|matematica|fisica|quimica|biologia)\b', t):
            return IntentResult(Intent.EDUCATIONAL_EXPLANATION.value, .96, 'educational')
        if re.search(r'\b(resuma|resumir|sintetize|principais pontos)\b', t):
            return IntentResult(Intent.SUMMARIZATION.value, .91, 'summary')
        if re.search(r'\b(plano|planeje|cronograma|rotina|revisao|flashcard|simulado)\b', t):
            return IntentResult(Intent.PLANNING.value, .90, 'planning')
        if re.search(r'\b(audio|transcreva|voz|aula gravada)\b', t):
            return IntentResult(Intent.AUDIO_TRANSCRIPTION.value, .88, 'audio')
        if re.search(r'\b(pdf|arquivo|documento|apostila|material)\b', t):
            return IntentResult(Intent.PDF_ANALYSIS.value, .87, 'pdf')
        if re.search(r'\b(pesquise|procure|fontes|artigos|pubmed)\b', t):
            return IntentResult(Intent.RESEARCH.value, .88, 'research')
        if re.search(r'^(oi|ola|olÃ¡|bom dia|boa tarde|boa noite)$', t):
            return IntentResult(Intent.CONVERSATION.value, .95, 'greeting')
        return IntentResult(Intent.CONVERSATION.value, .72, 'conversation')