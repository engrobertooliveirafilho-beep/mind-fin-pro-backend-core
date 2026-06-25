from __future__ import annotations

def norm(text: str) -> str:
    return (text or "").strip().lower()

def is_fitness(text: str) -> bool:
    t = norm(text)
    return any(x in t for x in [
        "emagrecer", "perder peso", "secar", "treino", "academia",
        "musculação", "musculacao", "dieta", "cardio", "hipertrofia",
        "ganhar massa", "gordura", "barriga"
    ])

def is_fitness_followup(text: str) -> bool:
    t = norm(text)
    return t in [
        "quais", "quais?", "quais são", "quais sao",
        "prossiga", "continue", "continua", "e depois",
        "explique melhor", "explica melhor", "monte um plano"
    ]

def reply(text: str) -> str:
    t = norm(text)

    if "quais" in t:
        return "Pra montar seu plano, preciso de: peso atual, altura, idade, dias de treino por semana, objetivo principal e se tem lesão em joelho, ombro, coluna ou cotovelo."

    if "prossiga" in t or "continue" in t or "continua" in t or "e depois" in t or "explique melhor" in t:
        return "Próximo passo: ajustar alimentação, musculação e cardio. Primeiro mantenha proteína em todas as refeições, treino de força 3 a 5 vezes por semana e cardio progressivo. Agora me passe peso, altura, idade, dias disponíveis e lesões."

    if "plano" in t or "monte" in t:
        return "Fechado. Plano inicial: musculação 3 a 5x por semana, cardio 2 a 4x, proteína diária e déficit calórico leve. Para personalizar, me diga peso, altura, idade, dias de treino e lesões."

    return "Dá para começar. Para emagrecer bem, o foco é déficit leve, treino de força, cardio progressivo e consistência. Me diga peso, altura, idade, dias de treino e lesões."
