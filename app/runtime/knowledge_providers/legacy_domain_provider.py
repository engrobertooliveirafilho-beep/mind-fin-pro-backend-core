from app.runtime.knowledge_providers.contract import KnowledgePacket


def build_domain_knowledge(inbound_text: str, domain: str = "") -> KnowledgePacket:
    t = (inbound_text or "").lower()
    d = (domain or "").lower()

    if "boi" in t or "confinamento" in t or d == "agro":
        return KnowledgePacket(
            domain="agro_confinamento",
            intent="automation_planning",
            facts=[
                "confinamento depende de trato, água, peso e observação",
                "o maior ganho inicial costuma estar no trato",
                "sensores e painel reduzem ronda manual repetitiva",
            ],
            steps=[
                "controle de nível no silo",
                "balança para ingredientes",
                "misturador ou vagão com rotina por lote",
                "leitura de cocho",
                "monitoramento de bebedouro",
                "balança de passagem",
                "dashboard e alerta no WhatsApp",
            ],
            priorities=[
                "começar por alimentação/trato",
                "validar consumo antes de avançar para câmera ou IA",
            ],
            source="bope4_extracted_from_whatsapp_legacy",
        )

    if "classe a" in t or "mercedes" in t or "marcha" in t or "ré" in t or "aks" in t or d == "automotivo":
        return KnowledgePacket(
            domain="automotivo_mercedes_aks",
            intent="diagnostic_sequence",
            facts=[
                "se as marchas entram desligado e travam ligado, o foco é desacoplamento da embreagem",
                "atuador AKS, curso, garfo, rolamento, fluido, sangria e regulagem devem ser verificados",
            ],
            steps=[
                "validar curso do atuador",
                "fazer sangria correta",
                "conferir sensor e regulagem",
                "só depois trocar peça",
            ],
            warnings=[
                "não comprar peça antes de validar causa provável",
            ],
            source="bope4_extracted_from_whatsapp_legacy",
        )

    if "marketing" in t or "criativo" in t or "oferta" in t or d == "marketing":
        return KnowledgePacket(
            domain="marketing_digital",
            intent="campaign_planning",
            facts=[
                "campanha depende de público, dor, promessa, prova, oferta e criativo",
            ],
            steps=[
                "definir público",
                "escolher promessa clara",
                "criar três ângulos de criativo",
                "rodar teste pequeno",
                "cortar o pior",
                "escalar o melhor",
            ],
            priorities=[
                "começar pela dor, oferta e gancho antes do layout",
            ],
            source="bope4_extracted_from_whatsapp_legacy",
        )

    if "trader" in t or "ftmo" in t or "paper" in t or "backtest" in t or d == "trader":
        return KnowledgePacket(
            domain="trader",
            intent="paper_validation",
            constraints=[
                "PAPER_ONLY",
                "LIVE/REAL/FTMO_REAL proibido antes de certificação",
            ],
            steps=[
                "rodar backtest limpo",
                "validar drawdown",
                "validar payoff",
                "validar frequência",
                "validar estabilidade por ativo",
                "ir para simulação controlada",
            ],
            warnings=[
                "bloquear overfit",
                "não operar real antes de certificação",
            ],
            source="bope4_extracted_from_whatsapp_legacy",
        )

    return KnowledgePacket(
        domain=d or "general",
        intent="contextual_response",
        facts=[],
        steps=[],
        priorities=["usar contexto ativo e gerar resposta natural"],
        source="bope4_default",
    )
