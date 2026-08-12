def _detect_simulation_domain(goal: str) -> str:
    text = (goal or "").lower()

    if any(x in text for x in ["eldora", "lançar", "lancar", "lançamento", "lancamento", "marketing", "instagram", "tiktok", "whatsapp"]):
        return "digital_launch"

    if any(x in text for x in ["trader", "trade", "ftmo", "backtest", "paper", "mercado"]):
        return "mind_trader"

    if any(x in text for x in ["treino", "academia", "dieta", "emagrecer", "musculação", "musculacao"]):
        return "fitness"

    if any(x in text for x in ["estudo", "estudar", "prova", "concurso", "faculdade"]):
        return "study"

    return "general_strategy"


def _scenario(name: str, probability: float, impact: str, description: str, risks=None, metrics=None):
    return {
        "name": name,
        "probability": probability,
        "impact": impact,
        "description": description,
        "risks": risks or [],
        "metrics": metrics or []
    }


def run_simulation(goal=None, context=None):
    goal = goal or "undefined_goal"
    context = context or {}
    domain = _detect_simulation_domain(goal)

    if domain == "digital_launch":
        scenarios = [
            _scenario(
                "conservador",
                0.35,
                "baixo_medio",
                "A Eldora gera curiosidade, mas a conversão inicial é baixa porque a promessa ainda precisa ser ajustada.",
                ["baixa_clareza_da_oferta", "pouca_retencao", "conteudo_sem_cta"],
                ["taxa_resposta_whatsapp", "retencao_24h", "intencao_pagamento"]
            ),
            _scenario(
                "provavel",
                0.50,
                "medio",
                "A audiência entende o uso principal, interage pelo WhatsApp e começa a repetir perguntas de estudo, treino e organização.",
                ["volume_suporte", "respostas_genericas", "custo_aquisicao"],
                ["conversas_iniciadas", "usuarios_recorrentes", "objeções_pagamento"]
            ),
            _scenario(
                "agressivo",
                0.15,
                "alto",
                "O conteúdo viraliza e gera pico de tráfego antes da operação estar pronta para suportar volume.",
                ["sobrecarga_runtime", "quebra_continuidade", "promessa_exagerada"],
                ["pico_mensagens", "latencia_resposta", "falhas_continuidade"]
            )
        ]

        risks = [
            "promessa_exagerada",
            "baixa_retencao",
            "alto_custo_aquisicao",
            "sobrecarga_suporte",
            "resposta_generica"
        ]

        recommendation = "Rodar canary com 10 a 30 conversas controladas antes de ampliar tráfego."

    elif domain == "mind_trader":
        scenarios = [
            _scenario(
                "conservador",
                0.45,
                "baixo",
                "As estratégias mantêm robustez limitada e seguem apenas em paper/backtest.",
                ["edge_fraco", "overfitting"],
                ["profit_factor", "drawdown", "walk_forward"]
            ),
            _scenario(
                "provavel",
                0.40,
                "medio",
                "Algumas hipóteses sobrevivem ao backtest, mas exigem stress test e validação paper prolongada.",
                ["degradacao", "slippage", "regras_ftmo"],
                ["payoff", "max_drawdown", "consistencia"]
            ),
            _scenario(
                "agressivo",
                0.15,
                "alto",
                "Um conjunto pequeno de estratégias parece forte, mas ainda não pode operar real sem certificação.",
                ["risco_execucao_real", "violacao_regras", "falso_positivo"],
                ["robustez", "decay", "paper_consistency"]
            )
        ]

        risks = [
            "overfitting",
            "drawdown_alto",
            "violacao_regras_ftmo",
            "ordem_real_nao_autorizada"
        ]

        recommendation = "Manter LIVE/REAL bloqueado e validar apenas em paper até certificação."

    else:
        scenarios = [
            _scenario(
                "conservador",
                0.40,
                "baixo",
                "O plano funciona parcialmente e exige ajuste de escopo.",
                ["escopo_vago", "baixa_adesao"],
                ["execucao", "retencao", "custo"]
            ),
            _scenario(
                "provavel",
                0.45,
                "medio",
                "O plano gera sinal suficiente para continuar em modo controlado.",
                ["dependencias", "execucao_incompleta"],
                ["sinal_usuario", "qualidade", "tempo"]
            ),
            _scenario(
                "agressivo",
                0.15,
                "alto",
                "O plano ganha tração antes de maturidade operacional.",
                ["sobrecarga", "falha_operacional"],
                ["volume", "latencia", "falhas"]
            )
        ]

        risks = [
            "escopo_vago",
            "metricas_fracas",
            "execucao_sem_evidencia"
        ]

        recommendation = "Executar piloto controlado e medir evidência antes de escalar."

    return {
        "status": "ok",
        "goal": goal,
        "context": context,
        "domain": domain,
        "prediction": {
            "confidence": 0.72 if domain != "general_strategy" else 0.62,
            "mode": "scenario_based_enriched",
            "recommended_scenario": "provavel"
        },
        "scenarios": scenarios,
        "risk_flags": risks,
        "recommendation": recommendation
    }


def simulation_health():
    return {
        "status": "ok",
        "engine": "predictive_simulation_engine",
        "mode": "scenario_based_enriched"
    }


def simulation_report():
    return {
        "status": "ok",
        "engine": "predictive_simulation_engine",
        "capabilities": [
            "domain_detection",
            "scenario_generation",
            "risk_flags",
            "recommendation"
        ],
        "modes": [
            "digital_launch",
            "mind_trader",
            "general_strategy"
        ]
    }
