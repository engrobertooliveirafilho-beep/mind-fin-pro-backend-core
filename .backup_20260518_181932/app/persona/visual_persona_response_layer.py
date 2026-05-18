from dataclasses import dataclass

@dataclass
class VisualPersonaResponse:
    text: str
    status: str = "VISUAL_PERSONA_RESPONSE_LAYER_OPERATIONAL"

class VisualPersonaResponseLayer:
    def answer(self, question: str, visual_context: str = "", memory_context: str = "") -> VisualPersonaResponse:
        q = (question or "").lower()
        base = visual_context or memory_context or "a identidade visual anterior da Neura"
        if "confi" in q:
            text = "Esse rosto precisa transmitir calma, simetria e presença humana sem parecer artificial demais. Eu manteria expressão suave, olhar direto, pele natural e reduziria elementos muito tecnológicos. Isso aumenta confiança porque parece uma presença útil, não uma máquina tentando impressionar."
        elif "humana" in q or "futurista" in q:
            text = "Ela está no ponto híbrido: humana o bastante para criar aproximação e futurista o bastante para comunicar IA. Para adoção em massa, eu deixaria 70% humana e 30% tecnológica. Esse equilíbrio reduz resistência e preserva diferenciação de marca."
        elif "transmite" in q or "achou" in q:
            text = "O rosto transmite inteligência calma, sofisticação e acessibilidade. Funciona bem para uma IA que precisa ensinar, orientar e criar vínculo sem parecer fria. O risco é ficar premium demais; por isso a expressão precisa parecer próxima, não distante."
        elif "aceit" in q or "resist" in q:
            text = "Sim, ajuda. Pessoas aceitam melhor uma IA quando ela parece previsível, amigável e visualmente estável. Um rosto consistente cria memória emocional: o usuário sente que está falando com a mesma presença, não com um robô genérico."
        else:
            text = "Minha leitura estratégica: a persona visual deve parecer confiável, humana e memorável. O rosto precisa manter identidade fixa, expressão acolhedora e estética limpa. Mudanças devem ser pequenas, sempre preservando reconhecimento."
        return VisualPersonaResponse(text=text)
