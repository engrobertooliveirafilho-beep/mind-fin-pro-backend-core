from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

STORE = Path("_runtime_state/companionship_profile_by_sender.json")

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _norm(text: str) -> str:
    return (text or "").strip().lower()

def _load() -> Dict[str, Any]:
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save(data: Dict[str, Any]) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_profile(sender: str) -> Dict[str, Any]:
    data = _load()
    sid = sender or "unknown"
    return data.get(sid, {
        "sender": sid,
        "created_at": _now(),
        "updated_at": _now(),
        "episodes": [],
        "semantic_self": {
            "known_goals": [],
            "known_projects": [],
            "known_constraints": [],
            "preferences": [],
            "health_notes": [],
            "social_context": []
        },
        "emotional_trajectory": [],
        "relationship_graph": {
            "domains": {},
            "people": {},
            "projects": {},
            "goals": {}
        },
        "care_flags": [],
        "conversation_style": {
            "prefers_direct": True,
            "prefers_depth": True,
            "needs_followup_questions": True
        },
        "trust": {
            "consistency_score": 0.0,
            "last_certified_at": None
        }
    })

def save_profile(sender: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    data = _load()
    sid = sender or "unknown"
    profile["sender"] = sid
    profile["updated_at"] = _now()
    data[sid] = profile
    _save(data)
    return profile

def _append_unique(lst: List[str], value: str, limit: int = 30) -> None:
    v = (value or "").strip()
    if not v:
        return
    if v not in lst:
        lst.append(v)
    del lst[:-limit]

def _episode(profile: Dict[str, Any], domain: str, subject: str, text: str, emotion: str) -> None:
    eps = profile.setdefault("episodes", [])
    eps.append({
        "timestamp": _now(),
        "domain": domain or "unknown",
        "subject": subject or "",
        "user_text": text or "",
        "emotion": emotion or "neutral"
    })
    del eps[:-80]

def detect_emotion(text: str) -> Dict[str, Any]:
    t = _norm(text)

    patterns = [
        ("frustrated", ["não consigo", "nao consigo", "deu ruim", "travou", "cansei", "difícil", "dificil", "não dá", "nao da"]),
        ("anxious", ["ansioso", "ansiedade", "preocupado", "medo", "tenso", "nervoso"]),
        ("tired", ["cansado", "exausto", "sem energia", "dormindo pouco", "sono ruim", "esgotado"]),
        ("confident", ["deu certo", "consegui", "boa", "fechou", "passou", "aprovado"]),
        ("motivated", ["vamos", "prossiga", "continuar", "quero evoluir", "bora"]),
        ("confused", ["não entendi", "nao entendi", "confuso", "como assim", "explique melhor"])
    ]

    for emo, keys in patterns:
        if any(k in t for k in keys):
            return {"emotion": emo, "confidence": 0.82}

    return {"emotion": "neutral", "confidence": 0.45}

def extract_semantic_facts(text: str) -> Dict[str, List[str]]:
    t = _norm(text)

    facts = {
        "known_goals": [],
        "known_projects": [],
        "known_constraints": [],
        "preferences": [],
        "health_notes": [],
        "social_context": []
    }

    if any(x in t for x in ["emagrecer", "perder peso", "secar", "86 kg", "86kg"]):
        facts["known_goals"].append("emagrecimento / composição corporal")

    if any(x in t for x in ["ftmo", "prop firm", "trader", "backtest", "estratégia", "estrategia"]):
        facts["known_goals"].append("evoluir operação trader / FTMO")
        facts["known_projects"].append("MIND Trader")

    if any(x in t for x in ["eldora", "whatsapp", "humanizar", "runtime", "conversação", "conversacao"]):
        facts["known_projects"].append("Eldora WhatsApp Runtime")

    if any(x in t for x in ["ombro", "cotovelo", "joelho", "coluna", "lesão", "lesao", "dor"]):
        facts["health_notes"].append("possível limitação física mencionada")

    if any(x in t for x in ["direto", "sem floreio", "na lata", "objetivo"]):
        facts["preferences"].append("respostas diretas e executáveis")

    if any(x in t for x in ["esposa", "filho", "família", "familia"]):
        facts["social_context"].append("contexto familiar relevante")

    if any(x in t for x in ["sem tempo", "correria", "muito trabalho", "sobrecarregado"]):
        facts["known_constraints"].append("carga cognitiva / tempo limitado")

    return facts

def infer_care_flags(text: str, emotion: str) -> List[str]:
    t = _norm(text)
    flags = []

    if emotion in ["tired", "anxious", "frustrated"]:
        flags.append("responder com cuidado antes de técnica")

    if any(x in t for x in ["dormindo pouco", "sem energia", "exausto", "esgotado"]):
        flags.append("priorizar recuperação, sono e ritmo sustentável")

    if any(x in t for x in ["dor", "lesão", "lesao", "ombro", "joelho", "cotovelo", "coluna"]):
        flags.append("evitar prescrição agressiva; sugerir cautela e ajuste seguro")

    if any(x in t for x in ["não sei mais", "nao sei mais", "não aguento", "nao aguento"]):
        flags.append("acolher sobrecarga e reduzir complexidade da resposta")

    return flags

def update_profile(sender: str, text: str, ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    profile = get_profile(sender)
    ctx = ctx or {}

    domain = ctx.get("active_domain") or "general"
    subject = ctx.get("active_subject") or text or ""

    emo = detect_emotion(text)
    emotion = emo["emotion"]

    facts = extract_semantic_facts(text)
    sem = profile.setdefault("semantic_self", {})

    for k, values in facts.items():
        sem.setdefault(k, [])
        for v in values:
            _append_unique(sem[k], v)

    profile.setdefault("emotional_trajectory", []).append({
        "timestamp": _now(),
        "emotion": emotion,
        "confidence": emo["confidence"],
        "text_sample": (text or "")[:160]
    })
    del profile["emotional_trajectory"][:-80]

    for flag in infer_care_flags(text, emotion):
        _append_unique(profile.setdefault("care_flags", []), flag, limit=30)

    graph = profile.setdefault("relationship_graph", {})
    graph.setdefault("domains", {})
    graph["domains"][domain] = graph["domains"].get(domain, 0) + 1

    for goal in sem.get("known_goals", []):
        graph.setdefault("goals", {})
        graph["goals"][goal] = graph["goals"].get(goal, 0) + 1

    for project in sem.get("known_projects", []):
        graph.setdefault("projects", {})
        graph["projects"][project] = graph["projects"].get(project, 0) + 1

    _episode(profile, domain, subject, text, emotion)

    trust = profile.setdefault("trust", {})
    trust["consistency_score"] = min(1.0, float(trust.get("consistency_score", 0.0)) + 0.03)
    trust["last_certified_at"] = _now()

    return save_profile(sender, profile)

def _sentence_limit(text: str, limit: int = 900) -> str:
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if len(t) <= limit:
        return t
    return t[:limit].rsplit(" ", 1)[0] + "."

def _subject_tokens(subject: str) -> List[str]:
    raw = re.findall(r"[a-zà-ÿ0-9]{3,}", _norm(subject))
    stop = {"quero", "como", "uma", "para", "com", "sem", "dos", "das", "que", "por", "mais", "isso", "esse", "essa"}
    return [x for x in raw if x not in stop][:8]

def build_subject_depth(subject: str, domain: str) -> str:
    t = _norm(subject)
    toks = _subject_tokens(subject)

    if "escola" in t and ("inglês" in t or "ingles" in t):
        return (
            "Para escola de inglês, eu separaria em 6 frentes: público-alvo, método de ensino, professores, estrutura, aquisição de alunos e margem. "
            "O primeiro número que eu buscaria é: quantos alunos pagantes você precisa para empatar o custo mensal."
        )

    if "franquia" in t:
        return (
            "Para franquia, eu validaria taxa inicial, royalties, margem real, ponto comercial, suporte da marca, payback e risco de fluxo de caixa. "
            "O erro comum é olhar faturamento e ignorar capital de giro."
        )

    if domain == "trader":
        return (
            "No trader, eu manteria a sequência: hipótese, ativo, timeframe, regra objetiva, risco por trade, backtest, robustez e simulação. "
            "Sem isso, parece avanço, mas vira aposta."
        )

    if domain == "fitness":
        return (
            "No físico, eu olharia primeiro rotina, sono, alimentação, lesões, treino de força e cardio. "
            "A prioridade é consistência sustentável, não agressividade."
        )

    if toks:
        return (
            f"Os pontos centrais aqui são: {', '.join(toks[:6])}. "
            "Eu transformaria isso em diagnóstico, plano prático, riscos e próximo passo mensurável."
        )

    return "Eu aprofundaria por objetivo, contexto, risco, restrição e próxima ação prática."

def compose_reply(sender: str, text: str, ctx: Dict[str, Any] | None, base_reply: str) -> str:
    profile = update_profile(sender, text, ctx)
    ctx = ctx or {}

    emotion = (profile.get("emotional_trajectory") or [{}])[-1].get("emotion", "neutral")
    sem = profile.get("semantic_self", {})
    subject = ctx.get("active_subject") or text or ""
    domain = ctx.get("active_domain") or "general"

    base = (base_reply or "").strip()

    care_prefix = ""
    if emotion in ["tired", "anxious", "frustrated"]:
        care_prefix = "Antes de ir para técnica pura, vou cuidar do ponto principal: seu ritmo e sua clareza importam aqui. "

    memory_hint = ""
    goals = sem.get("known_goals", [])
    health = sem.get("health_notes", [])
    if goals:
        memory_hint += f"Estou conectando isso com seu objetivo de {goals[-1]}. "
    if health and domain == "fitness":
        memory_hint += "E vou considerar cautela com possíveis limitações físicas. "

    depth = build_subject_depth(subject, domain)

    generic_markers = [
        "Vou continuar no mesmo contexto",
        "O próximo passo é aprofundar esse assunto",
        "Me diga se você quer checklist"
    ]

    if any(m.lower() in base.lower() for m in generic_markers):
        final = f"{care_prefix}{memory_hint}{depth}"
    else:
        final = f"{care_prefix}{memory_hint}{base}"

        if len(final) < 520 and domain not in ["fitness"]:
            final += " " + depth

    # presença sem ficar artificial
    if emotion == "confused":
        final += " Vou simplificar em passos menores para não virar confusão."
    elif emotion == "motivated":
        final += " Vamos manter avanço com critério, sem atropelar validação."

    return _sentence_limit(final, 950)
