from __future__ import annotations

def _norm(text: str) -> str:
    return str(text or "").strip().lower()

def classify_cognitive_frame(text: str, state: dict | None = None) -> dict:
    state = state or {}
    t = _norm(text)

    frame = {
        "intent": "general",
        "target": "world",
        "domain": state.get("domain") or "general",
        "goal": state.get("goal") or "",
        "phase": state.get("phase") or "open",
        "needs_realtime": False,
        "is_slot_fill": False,
        "reason": []
    }

    # target/system/capability
    if any(x in t for x in ["o que vc precisa", "o que você precisa", "pra fazer buscas", "para fazer buscas", "buscas reais", "por que não consegue", "porque não consegue", "o que falta"]):
        frame.update({
            "intent": "capability_question",
            "target": "eldora_system",
            "domain": "capability",
            "goal": "habilitar busca real",
            "phase": "diagnosis"
        })
        frame["reason"].append("system_capability_question")
        return frame

    # factual realtime
    if any(x in t for x in ["hoje", "agora", "último", "ultimo", "placar", "jogo", "escalação", "escalacao", "notícia", "noticia"]):
        frame["needs_realtime"] = True
        if any(x in t for x in ["jogo", "brasil", "futebol", "placar"]):
            frame["domain"] = "sports"
            frame["intent"] = "realtime_question"
            frame["goal"] = "responder fato atual"
            frame["target"] = "world"
            frame["reason"].append("realtime_sports")
            return frame

    # correction/meta
    if any(x in t for x in ["errou", "não entendi", "nao entendi", "frase pronta", "repete", "não é isso", "nao e isso"]):
        frame["intent"] = "correction"
        frame["target"] = "eldora_system"
        frame["phase"] = "repair"
        frame["reason"].append("user_correction")
        return frame

    # fitness goal
    if any(x in t for x in ["emagrecer", "secar", "dieta", "proteína", "proteina", "suplemento", "fisiculturista", "treino"]):
        frame["domain"] = "fitness"
        frame["target"] = "user"
        if any(x in t for x in ["monte", "monta", "dieta específica", "dieta especifica", "minha dieta"]):
            frame["intent"] = "create_plan"
            frame["goal"] = "montar dieta personalizada"
            frame["phase"] = "collecting_data"
        elif any(x in t for x in ["suplement"]):
            frame["intent"] = "supplement_question"
            frame["goal"] = state.get("goal") or "emagrecer"
            frame["phase"] = "advising"
        else:
            frame["intent"] = "goal_declaration"
            frame["goal"] = state.get("goal") or "emagrecer"
            frame["phase"] = "goal_start"
        frame["reason"].append("fitness_goal")
        return frame

    # slot fill after goal
    if state.get("domain") == "fitness" and any(x in t for x in ["kg", "anos", "refei", "treino", "altura", "1,"]):
        frame["domain"] = "fitness"
        frame["target"] = "user"
        frame["intent"] = "slot_fill"
        frame["goal"] = state.get("goal") or "montar dieta personalizada"
        frame["phase"] = "collecting_data"
        frame["is_slot_fill"] = True
        frame["reason"].append("fitness_slot_fill")
        return frame

    # followup
    if any(x in t for x in ["prossiga", "continue", "continua", "aprofunde", "detalhe", "pra que serve", "para que serve"]):
        frame["intent"] = "followup"
        frame["target"] = state.get("target") or "user"
        frame["domain"] = state.get("domain") or "general"
        frame["goal"] = state.get("goal") or ""
        frame["phase"] = "continuing"
        frame["reason"].append("followup_from_state")
        return frame

    if any(x in t for x in ["oi", "olá", "ola", "tudo bem"]):
        frame["intent"] = "social"
        frame["target"] = "user"
        frame["phase"] = "social"

    return frame
