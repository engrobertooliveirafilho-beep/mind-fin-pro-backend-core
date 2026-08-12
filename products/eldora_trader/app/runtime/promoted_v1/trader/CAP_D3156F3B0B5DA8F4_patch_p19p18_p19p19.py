from pathlib import Path
import re

path = Path("app/api/whatsapp.py")
src = path.read_text(encoding="utf-8")
original = src

block = r'''
# ============================================================
# P19P18/P19P19 - SHORT FOLLOWUP SEMANTIC CONTINUITY
# Objetivo:
# - Herda domínio ativo por sender_id.
# - Expande followup curto antes do cognitive pipeline.
# - Não depende de legacy flag.
# - Universal, não automotive-only.
# ============================================================

_P19P19_SENDER_DOMAIN_STATE = {}

_P19P19_SHORT_FOLLOWUPS = [
    "como eu faço", "como eu faco", "como faço", "como faco",
    "explique melhor", "explica melhor",
    "e depois", "depois",
    "continue", "continua",
    "detalhe", "detalha",
    "aprofunde", "aprofundar",
    "qual o primeiro passo", "primeiro passo",
    "por onde começo", "por onde comeco",
]

_P19P19_DOMAIN_KEYWORDS = {
    "confinamento_bovino": [
        "confinamento", "boi", "bois", "gado", "cocho", "trato",
        "silo", "ração", "racao", "bebedouro", "curral", "engorda",
        "balança", "balanca"
    ],
    "automotivo": [
        "mercedes", "classe a", "carro", "motor", "embreagem",
        "marcha", "cambio", "câmbio", "atuador", "ré", "re"
    ],
    "marketing": [
        "criativo", "anuncio", "anúncio", "copy", "campanha",
        "funil", "lead", "venda", "instagram", "tiktok", "sora"
    ],
    "trader": [
        "trade", "trader", "ftmo", "backtest", "payoff",
        "drawdown", "winrate", "paper", "estratégia", "estrategia"
    ],
}

_P19P19_DOMAIN_EXPANSION = {
    "confinamento_bovino": "automatização de confinamento de boi/gado com silo, balança, trato, cocho, bebedouro, pesagem e monitoramento",
    "automotivo": "diagnóstico automotivo do veículo mencionado, sem contaminar com equipamento agrícola",
    "marketing": "estratégia de marketing digital, criativos, copy, campanha e funil",
    "trader": "MIND Trader em modo PAPER_ONLY, backtest, estratégia e validação",
}

def _p19p19_norm(text):
    return str(text or "").strip().lower()

def _p19p19_is_short_followup(text):
    t = _p19p19_norm(text)
    t = t.replace("?", "").replace(".", "").replace("!", "").strip()
    return t in _P19P19_SHORT_FOLLOWUPS or (
        len(t.split()) <= 5 and any(x in t for x in [
            "depois", "continue", "detalhe", "aprofunde", "melhor", "como faço", "como faco"
        ])
    )

def _p19p19_detect_domain(text):
    t = _p19p19_norm(text)
    best_domain = None
    best_score = 0
    for domain, keys in _P19P19_DOMAIN_KEYWORDS.items():
        score = sum(1 for k in keys if k in t)
        if score > best_score:
            best_domain = domain
            best_score = score
    return best_domain

def _p19p19_remember_domain(sender_id, inbound_text):
    sender = str(sender_id or "default_sender")
    domain = _p19p19_detect_domain(inbound_text)
    if domain:
        _P19P19_SENDER_DOMAIN_STATE[sender] = {
            "domain": domain,
            "last_text": str(inbound_text or ""),
        }
    return domain

def _p19p19_get_domain(sender_id):
    sender = str(sender_id or "default_sender")
    state = _P19P19_SENDER_DOMAIN_STATE.get(sender) or {}
    return state.get("domain")

def _p19p19_expand_short_followup(sender_id, inbound_text):
    raw = str(inbound_text or "").strip()

    domain = _p19p19_detect_domain(raw)
    if domain:
        _p19p19_remember_domain(sender_id, raw)
        return raw

    if not _p19p19_is_short_followup(raw):
        return raw

    previous_domain = _p19p19_get_domain(sender_id)

    if not previous_domain:
        return raw

    context = _P19P19_DOMAIN_EXPANSION.get(previous_domain, previous_domain)

    return f"{raw} dentro do contexto anterior: {context}"

def _p19p19_direct_context_reply(sender_id, inbound_text):
    expanded = _p19p19_expand_short_followup(sender_id, inbound_text)
    domain = _p19p19_detect_domain(expanded) or _p19p19_get_domain(sender_id)

    if domain != "confinamento_bovino":
        return None

    t = _p19p19_norm(expanded)

    if any(x in t for x in ["como eu faço", "como eu faco", "como faço", "como faco", "primeiro passo"]):
        return (
            "Faça em fases. Primeiro automatize o trato: silo com sensor de nível, balança para pesar ingredientes "
            "e misturador/vagão com rotina por lote. Depois coloque leitura de cocho. Em seguida monitore água com sensor "
            "nos bebedouros. Por último, instale balança de passagem e alerte tudo no celular."
        )

    if any(x in t for x in ["explique melhor", "explica melhor", "detalhe", "detalha"]):
        return (
            "Na prática, o confinamento tem quatro rotinas críticas: comida, água, peso e observação. "
            "A automação entra nessa ordem: silo mede estoque, balança controla dieta, misturador prepara, "
            "cocho mostra sobra, bebedouro mostra consumo e balança mostra ganho de peso. O funcionário deixa de fazer ronda "
            "repetitiva e passa a supervisionar exceções."
        )

    if any(x in t for x in ["e depois", "depois", "continue", "continua"]):
        return (
            "Depois do trato, avance para água e pesagem. Sensor no bebedouro detecta falta de água ou consumo estranho. "
            "Balança de passagem mostra se o lote está ganhando peso. Com trato, água e peso monitorados, você já controla "
            "o confinamento quase inteiro por painel e alerta."
        )

    if any(x in t for x in ["aprofunde", "aprofundar"]):
        return (
            "A arquitetura completa é: sensor de nível no silo, balança de dieta, misturador controlado, distribuição por lote, "
            "câmera ou checklist digital no cocho, hidrômetro no bebedouro, balança de passagem, dashboard e alerta no WhatsApp. "
            "Não comece por câmera ou IA. Comece por alimentação, porque é onde está o maior custo e o maior ganho operacional."
        )

    return None
# /P19P18_P19P19_SHORT_FOLLOWUP_SEMANTIC_CONTINUITY
'''

if "P19P18/P19P19 - SHORT FOLLOWUP SEMANTIC CONTINUITY" not in src:
    marker = "# P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR"
    idx = src.find(marker)
    if idx == -1:
        raise RuntimeError("Marcador P19P16 não encontrado.")
    src = src[:idx] + block + "\n\n" + src[idx:]

# Inserir chamada cedo dentro de eldora_primary_runtime_reply
needle = 'def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):\n'
inject = '''def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):
    # P19P18/P19P19 early short-followup context continuity
    try:
        _p19p19_context_reply = _p19p19_direct_context_reply(sender_id, inbound_text)
        if _p19p19_context_reply:
            return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p19_context_reply, "")
    except Exception:
        pass
'''

if needle in src and "early short-followup context continuity" not in src:
    src = src.replace(needle, inject, 1)

# Corrige retorno final automotive-only para guard universal existente.
src = src.replace(
    'return _p19p3_apply_automotive_guards(inbound_text, visible.get("answer","") if isinstance(visible, dict) else str(visible), str(visible))',
    'return _p19p9_universal_whatsapp_output_guard(inbound_text, visible.get("answer","") if isinstance(visible, dict) else str(visible), str(visible))'
)

src = src.replace(
    'return _p19p3_apply_automotive_guards(inbound_text, str(visible.get("answer","")) if isinstance(visible,dict) else str(visible), str(visible))',
    'return _p19p9_universal_whatsapp_output_guard(inbound_text, str(visible.get("answer","")) if isinstance(visible,dict) else str(visible), str(visible))'
)

path.write_text(src, encoding="utf-8")

print({
    "changed": src != original,
    "file": str(path),
    "mission": "P19P18_P19P19_SHORT_FOLLOWUP_CONTEXT_FIX"
})
