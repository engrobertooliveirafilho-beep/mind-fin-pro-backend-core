class VisionDomainRouter:

    def detect(self, user_message="", base_hint=""):
        text = f"{user_message} {base_hint}".lower()

        if any(k in text for k in ["banner", "flyer", "instituto", "marca", "marketing", "anuncio", "anúncio", "campanha", "landing", "produto"]):
            return "marketing_ecosystem"

        if any(k in text for k in ["carro", "veiculo", "veículo", "modelo", "ano", "placa", "pneu", "roda"]):
            return "automotive"

        if any(k in text for k in ["sala", "arquitetura", "interior", "cowork", "deck", "lounge", "auditorio", "auditório", "cafe", "café"]):
            return "architecture"

        if any(k in text for k in ["pdf", "documento", "contrato", "planilha", "slide", "word", "excel", "powerpoint"]):
            return "document_analysis"

        return "general"

    def prompt_for(self, domain):
        if domain == "marketing_ecosystem":
            return """
Analise a imagem como estrategista sênior de marketing, branding e produto.

Obrigatório:
1. Identifique a proposta de valor.
2. Avalie clareza da oferta.
3. Avalie público-alvo provável.
4. Avalie diferenciais competitivos.
5. Avalie narrativa emocional.
6. Avalie arquitetura visual da peça.
7. Aponte riscos de comunicação.
8. Sugira melhorias práticas para conversão.
9. Dê uma nota de 0 a 10 para potencial comercial.
10. Seja específico, direto e estratégico.
"""

        if domain == "automotive":
            return """
Analise a imagem como perito automotivo visual.

Obrigatório:
1. Identifique tipo de veículo.
2. Estime marca/modelo provável, se possível.
3. Estime faixa de ano com incerteza.
4. Avalie estado externo visível.
5. Avalie pneus, rodas, faróis, pintura e alinhamento visual.
6. Diga o que não é possível confirmar pela imagem.
7. Use linguagem de probabilidade, não certeza absoluta.
"""

        if domain == "architecture":
            return """
Analise a imagem como arquiteto e consultor de experiência espacial.

Obrigatório:
1. Avalie layout.
2. Avalie fluxo de pessoas.
3. Avalie iluminação.
4. Avalie materiais e atmosfera.
5. Avalie integração com natureza.
6. Avalie funcionalidade comercial.
7. Sugira melhorias práticas.
"""

        if domain == "document_analysis":
            return """
Analise a imagem como analista documental.

Obrigatório:
1. Extraia informações principais.
2. Organize em tópicos.
3. Aponte dados relevantes.
4. Identifique inconsistências.
5. Sugira próximos passos.
"""

        return """
Faça uma análise visual avançada e honesta.
Descreva o que aparece, detalhe elementos relevantes, aponte incertezas e diga o que não dá para confirmar.
"""
