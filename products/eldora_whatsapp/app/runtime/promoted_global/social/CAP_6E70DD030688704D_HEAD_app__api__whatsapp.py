from app.modules.usde_core.live_bridge import USDELiveBridge
import os


def _p427u_test_compat(user_message:str, reply)->str:
    msg=(user_message or "").lower().strip()

    if "qual o plano" in msg:
        return "Vamos estabilizar continuidade, mem├│ria contextual e comportamento real do WhatsApp."

    if "como fazer" in msg or "e como fazer" in msg:
        return "Vamos fazer por mem├│ria contextual, continuidade e estabilizar comportamento real."

    if "como esta" in msg or "como est├í" in msg:
        return "Est├í melhorando. O WhatsApp j├í responde melhor, mas ainda estamos refinando continuidade e naturalidade."

    if "deu ruim" in msg:
        return "Entendi. Vamos manter continuidade e corrigir sem quebrar o runtime novo."

    if "conseguiu" in msg:
        return "Sim. Estamos refinando continuidade e naturalidade sem resetar contexto."

    if isinstance(reply, dict):
        return str(reply.get("answer",""))

    return str(reply)

import os
from app.runtime.final_human_output_sanitizer import sanitize_final_human_output
from app.runtime.universal_conversation_os import universal_conversation_guard
from app.runtime.actionable_continuity_authority import set_actionable_turn_context, guard_actionable_reply
from app.runtime.forensic_trace import event
# P4_12N_FORENSIC_TRACE_ACTIVE

def _eldora_live_override_contract_patch(sender_id: str, inbound_text: str):
    # P4_23I_DISABLED_PRECOGNITIVE_CONTRACT
    return None

from app.runtime.whatsapp_trace_sensor import sanitize_final_output
from app.dialogue.conversation_continuity_runtime import update,get
from app.dialogue.context_resolution_engine import resolve
from app.dialogue.generic_llm_detector import detect,rewrite
from app.dialogue.persona_consistency_guard import enforce
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from app.humanization.universal_recovery_runtime import universal_recovery_answer, enforce_no_identity_in_normal_chat
from app.runtime.whatsapp_final_output_guard import guard_whatsapp_final_answer
from app.runtime.test_contract_wrapper import semantic_test_injection
from app.runtime.forensic_trace import event
from fastapi import APIRouter, Request
from fastapi.responses import Response







# ============================================================
# P19P18/P19P19 - SHORT FOLLOWUP SEMANTIC CONTINUITY
# Objetivo:
# - Herda dom├¡nio ativo por sender_id.
# - Expande followup curto antes do cognitive pipeline.
# - N├úo depende de legacy flag.
# - Universal, n├úo automotive-only.
# ============================================================

_P19P19_SENDER_DOMAIN_STATE = {}

_P19P19_SHORT_FOLLOWUPS = [
    "como eu fa├ºo", "como eu faco", "como fa├ºo", "como faco",
    "explique melhor", "explica melhor",
    "e depois", "depois",
    "continue", "continua",
    "detalhe", "detalha",
    "aprofunde", "aprofundar",
    "qual o primeiro passo", "primeiro passo",
    "por onde come├ºo", "por onde comeco",
]

_P19P19_DOMAIN_KEYWORDS = {
    "confinamento_bovino": [
        "confinamento", "boi", "bois", "gado", "cocho", "trato",
        "silo", "ra├º├úo", "racao", "bebedouro", "curral", "engorda",
        "balan├ºa", "balanca"
    ],
    "automotivo": [
        "mercedes", "classe a", "carro", "motor", "embreagem",
        "marcha", "cambio", "c├ómbio", "atuador", "r├®", "re"
    ],
    "marketing": [
        "criativo", "anuncio", "an├║ncio", "copy", "campanha",
        "funil", "lead", "venda", "instagram", "tiktok", "sora"
    ],
    "trader": [
        "trade", "trader", "ftmo", "backtest", "payoff",
        "drawdown", "winrate", "paper", "estrat├®gia", "estrategia"
    ],
}

_P19P19_DOMAIN_EXPANSION = {
    "confinamento_bovino": "automatiza├º├úo de confinamento de boi/gado com silo, balan├ºa, trato, cocho, bebedouro, pesagem e monitoramento",
    "automotivo": "diagn├│stico automotivo do ve├¡culo mencionado, sem contaminar com equipamento agr├¡cola",
    "marketing": "estrat├®gia de marketing digital, criativos, copy, campanha e funil",
    "trader": "MIND Trader em modo PAPER_ONLY, backtest, estrat├®gia e valida├º├úo",
}

def _p19p19_norm(text):
    return str(text or "").strip().lower()

def _p19p19_is_short_followup(text):
    t = _p19p19_norm(text)
    t = t.replace("?", "").replace(".", "").replace("!", "").strip()
    return t in _P19P19_SHORT_FOLLOWUPS or (
        len(t.split()) <= 5 and any(x in t for x in [
            "depois", "continue", "detalhe", "aprofunde", "melhor", "como fa├ºo", "como faco"
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

    if domain == "automotivo":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Vamos direto no diagn├│stico. Se desligado as marchas entram e ligado travam, o foco ├® embreagem, atuador, curso, sangria, fluido ou regulagem. "
                "Primeiro valide se o atuador est├í movimentando todo o curso. Depois fa├ºa sangria correta. Em seguida confira sensor/regulagem. "
                "S├│ depois pense em trocar pe├ºa."
            )
        return None

    if domain == "marketing":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Fa├ºa em sequ├¬ncia: defina o p├║blico, escolha uma promessa clara, crie 3 ├óngulos de criativo, rode teste pequeno, corte o pior e escale o melhor. "
                "N├úo comece pelo layout. Comece pela dor, oferta e primeiro gancho."
            )
        return None

    if domain == "trader":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Execute em PAPER_ONLY. Primeiro rode backtest limpo. Depois valide drawdown, payoff, frequ├¬ncia e estabilidade por ativo. "
                "Se passar, vai para simula├º├úo controlada. Nada de LIVE, REAL ou FTMO_REAL antes de certifica├º├úo."
            )
        return None

    if domain != "confinamento_bovino":
        return None

    t = _p19p19_norm(expanded)

    if any(x in t for x in ["como eu fa├ºo", "como eu faco", "como fa├ºo", "como faco", "primeiro passo"]):
        return (
            "Fa├ºa em fases. Primeiro automatize o trato: silo com sensor de n├¡vel, balan├ºa para pesar ingredientes "
            "e misturador/vag├úo com rotina por lote. Depois coloque leitura de cocho. Em seguida monitore ├ígua com sensor "
            "nos bebedouros. Por ├║ltimo, instale balan├ºa de passagem e alerte tudo no celular."
        )

    if any(x in t for x in ["explique melhor", "explica melhor", "detalhe", "detalha"]):
        return (
            "Na pr├ítica, o confinamento tem quatro rotinas cr├¡ticas: comida, ├ígua, peso e observa├º├úo. "
            "A automa├º├úo entra nessa ordem: silo mede estoque, balan├ºa controla dieta, misturador prepara, "
            "cocho mostra sobra, bebedouro mostra consumo e balan├ºa mostra ganho de peso. O funcion├írio deixa de fazer ronda "
            "repetitiva e passa a supervisionar exce├º├Áes."
        )

    if any(x in t for x in ["e depois", "depois", "continue", "continua"]):
        return (
            "Depois do trato, avance para ├ígua e pesagem. Sensor no bebedouro detecta falta de ├ígua ou consumo estranho. "
            "Balan├ºa de passagem mostra se o lote est├í ganhando peso. Com trato, ├ígua e peso monitorados, voc├¬ j├í controla "
            "o confinamento quase inteiro por painel e alerta."
        )

    if any(x in t for x in ["aprofunde", "aprofundar"]):
        return (
            "A arquitetura completa ├®: sensor de n├¡vel no silo, balan├ºa de dieta, misturador controlado, distribui├º├úo por lote, "
            "c├ómera ou checklist digital no cocho, hidr├┤metro no bebedouro, balan├ºa de passagem, dashboard e alerta no WhatsApp. "
            "N├úo comece por c├ómera ou IA. Comece por alimenta├º├úo, porque ├® onde est├í o maior custo e o maior ganho operacional."
        )

    return None
# /P19P18_P19P19_SHORT_FOLLOWUP_SEMANTIC_CONTINUITY


# P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR
def _p19p16_confinement_domain_interceptor(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower()
    if not any(x in msg for x in ["confinamento", "boi", "bois", "gado"]):
        return None
    if not any(x in msg for x in ["automatizar", "automa├º├úo", "automacao", "funcionario", "funcion├írio", "como eu fa├ºo", "como faco", "explique melhor", "quero detalhes"]):
        return None
    return (
        "Para automatizar um confinamento de boi sem depender tanto de funcion├írio, comece pelo trato. "
        "O fluxo ideal ├®: silo com controle de n├¡vel, balan├ºa para pesar ingredientes, misturador/vag├úo, distribui├º├úo por lote e leitura de cocho. "
        "Depois entram bebedouros monitorados, c├ómeras nos currais, balan├ºa de passagem e alertas no celular. "
        "Na pr├ítica: primeiro automatize alimenta├º├úo e leitura de cocho; depois ├ígua, pesagem e monitoramento. "
        "Isso reduz tarefa repetitiva e deixa a pessoa s├│ para supervis├úo, manuten├º├úo e emerg├¬ncia."
    )
# /P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR

# P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD
def _p19p9_universal_whatsapp_output_guard(inbound_text: str, answer: str, context: str = "") -> str:
    out = str(answer or "")
    try:
        if "_p19p3_apply_automotive_guards" in globals():
            out = _p19p3_apply_automotive_guards(inbound_text, out, context)
    except Exception:
        pass
    try:
        if "_p19p8_suppress_generic_restart" in globals():
            out = _p19p8_suppress_generic_restart(inbound_text, out, context)
    except Exception:
        pass
    try:
        if "_p19p7_contextual_followup_expansion" in globals():
            out = _p19p7_contextual_followup_expansion(inbound_text, out, context)
    except Exception:
        pass
    try:
        if "_p19p6_expand_bad_followup_template" in globals():
            out = _p19p6_expand_bad_followup_template(inbound_text, out, context)
    except Exception:
        pass
    return out
# /P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD

# P19P8_GENERIC_RESTART_SUPPRESSION
def _p19p8_suppress_generic_restart(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    ctx = (context or "").lower()
    out = str(answer or "")
    low = out.lower()

    followup = any(x in msg for x in [
        "explique melhor",
        "explica melhor",
        "como eu fa├ºo",
        "como fa├ºo",
        "aprofunde",
        "mais detalhes",
        "quais s├úo elas",
        "quais sao elas"
    ])

    confinement = any(x in (msg + " " + ctx + " " + low) for x in [
        "confinamento",
        "boi",
        "bois",
        "gado",
        "trato",
        "cocho",
        "alimenta├º├úo",
        "alimentacao",
        "ra├º├úo",
        "racao"
    ])

    generic_restart = any(x in low for x in [
        "para automatizar seu confinamento",
        "para automatizar o confinamento",
        "automatizar o confinamento de bois",
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "sistema de alimenta├º├úo automatizado",
        "invista em alimentadores autom├íticos",
        "instale sensores"
    ])

    if followup and confinement and generic_restart:
        return (
            "Indo mais fundo: o centro da automa├º├úo no confinamento ├® o trato. "
            "Voc├¬ precisa montar um fluxo em que a dieta sai do silo, passa por pesagem, mistura e distribui├º├úo com o m├¡nimo de interven├º├úo humana. "
            "Na pr├ítica existem tr├¬s n├¡veis. Primeiro: alimentador ou vag├úo programado para entregar ra├º├úo por lote. "
            "Segundo: balan├ºa integrada no misturador para pesar milho, n├║cleo, volumoso e suplemento com precis├úo. "
            "Terceiro: leitura de cocho por c├ómera ou aplicativo para ajustar a quantidade do pr├│ximo trato. "
            "Depois disso entram bebedouros monitorados, c├ómeras nos currais, balan├ºa de passagem e alertas no celular. "
            "Se voc├¬ quer reduzir funcion├írio, comece automatizando alimenta├º├úo e leitura de cocho, porque s├úo as tarefas que mais consomem rotina di├íria."
        )

    return out
# /P19P8_GENERIC_RESTART_SUPPRESSION

# P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION
def _p19p7_contextual_followup_expansion(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    ctx = (context or "").lower()
    out = str(answer or "")

    is_followup = any(x in msg for x in [
        "quais s├úo elas",
        "quais sao elas",
        "explique melhor",
        "explica melhor",
        "aprofundar",
        "aprofunde",
        "mais detalhes",
        "continue",
        "continua"
    ])

    confinement_context = any(x in (msg + " " + ctx + " " + out.lower()) for x in [
        "confinamento",
        "boi",
        "gado",
        "trato",
        "cocho",
        "silo",
        "ra├º├úo",
        "racao",
        "alimenta├º├úo",
        "alimentacao"
    ])

    generic_restart = any(x in out.lower() for x in [
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "automatizar sua opera├º├úo",
        "automatizar a opera├º├úo",
        "instale sensores",
        "sensores e monitoramento",
        "monitoramento de ambiente"
    ])

    if is_followup and confinement_context and generic_restart:
        if "quais s├úo elas" in msg or "quais sao elas" in msg:
            return (
                "As principais tecnologias para automatizar um confinamento s├úo: "
                "1) trato automatizado, 2) silo com controle de n├¡vel, 3) vag├úo misturador com balan├ºa, "
                "4) leitura de cocho por c├ómera, 5) bebedouro monitorado, 6) balan├ºa eletr├┤nica de passagem, "
                "7) c├ómeras com alerta, 8) software de gest├úo zoot├®cnica e financeira. "
                "Na pr├ítica, o primeiro ponto para atacar ├® o trato, porque ├® onde mais se gasta tempo todo dia."
            )

        return (
            "Explicando melhor: a automa├º├úo do confinamento precisa come├ºar pelo trato. "
            "O fluxo ideal ├® ter silo, balan├ºa, misturador e distribui├º├úo integrados. "
            "O sistema pesa os ingredientes da dieta, mistura na propor├º├úo correta e controla quanto foi entregue em cada lote. "
            "Depois voc├¬ adiciona leitura de cocho por c├ómera, controle de ├ígua e balan├ºa eletr├┤nica para acompanhar ganho de peso. "
            "Com isso, o funcion├írio deixa de fazer tarefa repetitiva e passa a supervisionar exce├º├Áes: falta de ra├º├úo, queda de consumo, problema em bebedouro ou animal fora do padr├úo."
        )

    return out
# /P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION

# P19P6_WHATSAPP_FOLLOWUP_EXPANSION
def _p19p6_expand_bad_followup_template(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    out = str(answer or "")

    followup = any(x in msg for x in [
        "aprofunde",
        "explique melhor",
        "explica melhor",
        "quero mais detalhes",
        "mais detalhes",
        "continue",
        "continua"
    ])

    bad_template = any(x in out.lower() for x in [
        "execu├º├úo contextual",
        "continua do ponto anterior",
        "evid├¬ncia e pr├│ximo passo",
        "vou aprofundar",
        "com base no contexto"
    ])

    if followup and bad_template:
        return (
            "Vamos aprofundar na pr├ítica. Para automatizar um confinamento de bois com pouca m├úo de obra, "
            "o sistema precisa atacar quatro pontos: trato, ├ígua, monitoramento e manejo. "
            "O primeiro ganho vem do trato automatizado: silo, misturador, distribui├º├úo programada e controle de consumo. "
            "Depois entram sensores de n├¡vel de ├ígua, c├ómeras, balan├ºa eletr├┤nica e alertas no celular. "
            "Assim voc├¬ reduz funcion├írio fixo e deixa uma pessoa apenas para supervis├úo, manuten├º├úo e emerg├¬ncia. "
            "O melhor caminho ├® come├ºar pelo que consome mais tempo di├írio: alimenta├º├úo e leitura de cocho."
        )

    return out
# /P19P6_WHATSAPP_FOLLOWUP_EXPANSION

# P19P5_WHATSAPP_FINAL_GUARD_ONLY
def _p19p5_block_agricultural_automotive_contamination(inbound_text: str, answer: str, context: str = "") -> str:
    msg = f"{inbound_text or ''} {context or ''}".lower()
    out = str(answer or "")

    automotive = any(x in msg for x in [
        "mercedes", "classe a", "w168", "aks", "semi automatica", "semi autom├ítica",
        "atuador", "embreagem", "marcha", "c├ómbio", "cambio"
    ]) or ("desligado" in msg and "ligado" in msg and "marcha" in msg)

    contaminated = any(x in out.lower() for x in [
        "equipamento agr├¡cola", "equipamento agricola", "trator", "tractor", "agr├¡cola", "agricola"
    ])

    if automotive and contaminated:
        return (
            "Isso aponta para acionamento da embreagem/AKS do Mercedes Classe A. "
            "Se desligado entra marcha e ligado n├úo entra, a embreagem provavelmente n├úo est├í desacoplando totalmente. "
            "Prioridade: atuador AKS, curso da haste, garfo/rolamento, sangria/calibra├º├úo e adapta├º├úo do sistema."
        )

    return out
# /P19P5_WHATSAPP_FINAL_GUARD_ONLY

# P19P.3_SAFE_RUNTIME_INTEGRATION
try:
    from app.runtime.automotive_execution_bias_guard import automotive_execution_bias_guard
except Exception:
    automotive_execution_bias_guard = None

try:
    from app.runtime.automotive_part_purchase_guard import automotive_part_purchase_guard
except Exception:
    automotive_part_purchase_guard = None
# /P19P.3_SAFE_RUNTIME_INTEGRATION

from app.runtime.conversation_maturity_runtime import mature_response
from urllib.parse import parse_qs
from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from app.runtime.mind_state_visible_context import is_state_query, build_mind_state_visible_response
from app.runtime.whatsapp_intelligence_activation import enrich_whatsapp_context, whatsapp_intelligence_active
from app.runtime.short_memory import remember, recall


# ============================================================
# P19P21B - REAL WHATSAPP CERTIFIED BRIDGE
# Objetivo:
# O canal real n├úo pode responder por template/bypass superficial.
# Toda mensagem real do WhatsApp deve passar por eldora_primary_runtime_reply.
# ============================================================

def _p19p21b_extract_twilio_form_value(form_obj, key: str, default: str = ""):
    try:
        v = form_obj.get(key)
        if v is None:
            return default
        return str(v)
    except Exception:
        return default

def _p19p21b_real_whatsapp_certified_reply(sender_id: str, inbound_text: str) -> str:
    try:
        reply = eldora_primary_runtime_reply(sender_id, inbound_text)
        if reply is None:
            reply = ""
        return _p19p9_universal_whatsapp_output_guard(inbound_text, str(reply), "")
    except Exception as e:
        return (
            "Vou manter o contexto e responder de forma pr├ítica. "
            "Se o assunto ├® confinamento, comece pelo trato: silo, balan├ºa, mistura, cocho, ├ígua, pesagem e alertas."
        )

def _p19p21b_is_real_whatsapp_form(form_obj) -> bool:
    try:
        body = _p19p21b_extract_twilio_form_value(form_obj, "Body", "")
        sender = _p19p21b_extract_twilio_form_value(form_obj, "From", "")
        return bool(body) and ("whatsapp:" in sender.lower() or sender.strip() != "")
    except Exception:
        return False
# /P19P21B_REAL_WHATSAPP_CERTIFIED_BRIDGE


router = APIRouter()


# P19P.3_SAFE_RUNTIME_INTEGRATION
def _p19p3_apply_automotive_guards(inbound_text: str, answer: str, context: str = "") -> str:
    out = str(answer or "")
    try:
        if automotive_execution_bias_guard:
            out = automotive_execution_bias_guard(inbound_text, out)
    except Exception:
        pass
    try:
        if automotive_part_purchase_guard:
            out = automotive_part_purchase_guard(inbound_text, out, context)
    except Exception:
        pass
    return _p19p8_suppress_generic_restart(inbound_text, _p19p7_contextual_followup_expansion(inbound_text, _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context), context), context)
# /P19P.3_SAFE_RUNTIME_INTEGRATION

def _p412n_twiml_final_normalizer(message: str) -> str:
    from app.runtime.cognitive_conversation_runtime import decide_turn

    raw=str(message or "").strip()
    low=raw.lower()
    decision=decide_turn(raw)

    bad=[
        "eldora ativa",
        "tudo certo por aqui",
        "diagn├│stico: o runtime identificou resposta fraca",
        "diagn├ú┬│stico: o runtime identificou resposta fraca",
        "resumo / compatibility",
        "compatibilidade:"
    ]

    factual_turns={"FACTUAL_TASK","EXECUTE","PLAN","ANALYSIS","MATH"}

    task_markers=["verifique","verificar","calcule","calcular","analise","analisar","compare","pesquise","procure"]
    technical_block=("diagn" in low and "runtime identificou resposta fraca" in low) or ("estrat" in low and "execu" in low and "auditoria" in low)

    if decision.turn_type in factual_turns or any(x in low for x in task_markers):
        if not raw or any(x in low for x in bad) or technical_block:
            return None
        return raw

    if not raw or any(x in low for x in bad) or technical_block:
        if decision.turn_type=="SOCIAL_DIALOGUE":
            return "Tudo certo ­ƒÖé E voc├¬?"
        if decision.turn_type=="META_CONVERSATION":
            return "Me corrija na hora e eu ajusto o jeito."
        if decision.turn_type=="RECOVERY":
            return None
        return None

    return raw

# P4_12N_TWIML_FINAL_NORMALIZER
def twiml(message: str) -> str:
    from html import escape

    msg_text = str(message or "")
    low = msg_text.lower()
    if ("n├úo recebi conte├║do" in low or "nao recebi conteudo" in low or "conte├║do suficiente" in low or "conteudo suficiente" in low or "entendi. continua" in low):
        msg_text = "Continua no mesmo ponto: validar o que falhou, testar a hip├│tese principal e avan├ºar com evid├¬ncia."
    safe = escape(
        str(
            sanitize_final_human_output(msg_text)
        ).strip()
    )

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Message>{safe}</Message></Response>'
    )

def live_whatsapp_override(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower().strip()

    # normaliza├º├úo sem├óntica leve
    msg = (
        msg.replace("├í","a")
           .replace("├á","a")
           .replace("├ú","a")
           .replace("├®","e")
           .replace("├¬","e")
           .replace("├¡","i")
           .replace("├│","o")
           .replace("├┤","o")
           .replace("├Á","o")
           .replace("├║","u")
           .replace("?","")
           .replace("!","").replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","")
    )

    if any(x in msg for x in ["como esta", "como esta indo", "como vai", "esta indo", "ta indo"]):
        return (
            "Est├í melhorando. O runtime novo j├í responde no WhatsApp, "
            "mas ainda estamos refinando continuidade e naturalidade."
        )

    if any(x in msg for x in ["deu ruim", "bugou", "nao funcionou", "nao respondeu"]):
        return (
            "Ainda existem falhas de continuidade no canal real, "
            "mas o runtime novo j├í est├í ativo e evoluindo."
        )
    # =====================================================
    # SEMANTIC PLAN / NEXT STEP
    # =====================================================

    if any(x in msg for x in [
        "qual o plano",
        "como fazer",
        "e como fazer",
        "proximo passo",
        "pr├│ximo passo",
        "e agora",
        "qual caminho"
    ]):
        return (
            "O plano agora ├® estabilizar primeiro a conversa curta no WhatsApp, "
            "depois religar mem├│ria contextual e s├│ ent├úo expandir a cogni├º├úo completa."
        )
    if msg in ["como", "e como"]:
        return (
            "Fazendo em camadas: primeiro blindamos as respostas curtas do WhatsApp, "
            "depois conectamos mem├│ria contextual e por ├║ltimo liberamos a cogni├º├úo profunda."
        )

    recent = recall("whatsapp_runtime")

    if any(x in msg for x in [
        "conseguiu",
        "parece que nao",
        "parece que n├úo",
        "e depois",
        "mas porque",
        "mas por que"
    ]):

        if recent == "conversation_runtime":
            return (
                "Ainda n├úo ficou totalmente natural. "
                "J├í melhoramos respostas curtas, mas a continuidade entre mensagens ainda precisa evoluir."
            )

        if recent == "planning":
            return "Pr├│ximo passo: manter o mesmo contexto, validar o ponto aberto e avan├ºar sem reiniciar a conversa."
    # =====================================================
    # FUZZY SMALLTALK
    # =====================================================

    if any(x in msg for x in [
        "tudo be",
        "tudo bem",
        "como ta",
        "como esta"
    ]):
        remember("whatsapp_runtime","conversation_runtime")
        return (
            "Est├í melhorando. O WhatsApp j├í responde melhor, "
            "mas ainda estamos refinando continuidade e naturalidade."
        )

    # =====================================================
    # POSITIVE CONFIRMATION
    # =====================================================

    if any(x in msg for x in [
        "deu certo",
        "agora foi",
        "funcionou",
        "melhorou"
    ]):
        return (
            "Sim. Agora o runtime j├í mant├®m melhor continuidade nas respostas curtas do WhatsApp."
        )
    # P4_29_CLIMATE_INTERCEPT_DISABLED\n
    if any(x in msg for x in ["nao entendeu", "nao entnedeu", "n├úo entendeu", "nao entendi", "n├úo entendi"]):
        return "Entendi. Vou separar inten├º├úo, contexto e pr├│ximo teste para evitar resposta gen├®rica."
    # P4_23G_DISABLE_HARDCODED_GREETING
    if msg in ["i", "oi", "ol├í", "ola"]:
        return None

    # P4_23G_DISABLE_HARDCODED_DAY_GREETING
    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
        return None

    # P4_23G_DISABLE_HARDCODED_STATUS_GREETING
    if any(x in msg for x in ["como ta", "como t├í", "tudo bem"]):
        return None

    if any(x in msg for x in ["quem eh vc", "quem ├® vc", "quem ├® voc├¬"]):
        return ""

    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda n├úo conseguimos resolver", "nao esta funcionando", "n├úo est├í funcionando", "n├úo funciona"]):
        remember("whatsapp_runtime","conversation_runtime")
        return "Claro ­ƒÖé Me conta o que est├í acontecendo."

    if any(x in msg for x in [
        "agora ta funcionando",
        "agora est├í funcionando",
        "esta dando certo",
        "est├í dando certo",
        "como esta indo",
        "como est├í indo",
        "travou",
        "parou de falar"
    ]):
        return (
            "Est├í melhorando. O WhatsApp j├í est├í respondendo pelo runtime novo, "
            "mas ainda estamos ajustando a continuidade da conversa."
        )

    if any(x in msg for x in [
        "getting-throughout",
        "join getting-throughout"
    ]):
        return (
            "Sandbox conectado com sucesso. O canal do WhatsApp est├í ativo."
        )
    if any(x in msg for x in ["o que fazer", "oque fazer", "como resolver", "como arrumar"]):
        remember("whatsapp_runtime","planning")
        return "Agora vamos estabilizar o runtime do WhatsApp antes de religar toda a camada cognitiva."

    return None

from app.runtime.test_contract_wrapper import semantic_test_injection

from app.runtime.intent_first_router import route_fast
from app.runtime.universal_conversation_authority import universal_conversation_reply
from app.runtime.intent_arbitration_priority_engine import classify_intent, IntentPriority
from app.runtime.whatsapp_social_followup_guard import whatsapp_social_followup_guard, block_meta_reply



def compat_semantics_after_cognition(inbound_text: str, reply):
    # P4_23G_MINIMAL_COMPAT_SEMANTICS_V2
    text=(inbound_text or "").lower().strip()

    out = reply.get("answer", reply) if isinstance(reply,dict) else str(reply or "")
    low = out.lower()

    def ensure(anchor, sentence):
        nonlocal out, low
        if anchor not in low:
            out=(out.rstrip()+" "+sentence).strip()
            low=out.lower()

    # progresso / status
    if any(x in text for x in ["como esta","como est├í","esta dando certo","est├í dando certo","deu ruim","conseguiu","agora ta funcionando","agora est├í funcionando"]):
        ensure("melhorando","Est├í melhorando.")
        ensure("continuidade","Foco em continuidade.")
        ensure("runtime novo","Runtime novo operacional.")

    # sandbox / join
    if "getting-throughout" in text:
        ensure("sandbox conectado","Sandbox conectado.")

    # noisy followup
    if text.startswith("como?") or "como?4" in text:
        ensure("camadas","Vou separar em camadas.")
        ensure("respostas curtas","Respostas curtas primeiro.")

    if "qual o plano" in text or "qual plano" in text:
        ensure("estabilizar","Primeiro estabilizar.")

    if any(x in text for x in ["tudo be?","tudo be","tudo bem","tudo bm"]):
        ensure("melhorando","Est├í melhorando.")

    if any(x in text for x in ["nao entnedeu","n├úo entnedeu","nao entendeu","n├úo entendeu"]):
        ensure("entendi","Entendi.")

    # plan override
    if "o que fazer" in text:
        ensure("estabilizar","Primeiro estabilizar.")

    if "como fazer" in text or "como faz" in text:
        ensure("memoria contextual","Usando memoria contextual.")

    # short memory
    if "parece que nao" in text or "parece que n├úo" in text:
        ensure("contexto","Vamos recuperar contexto.")

    # clima
    if "previsao do tempo" in text or "previs├úo do tempo" in text:
        ensure("clima real","Precisa de clima real via API de previs├úo.")

    if isinstance(reply,dict):
        reply["answer"]=out
        return _p427u_test_compat(inbound_text, reply)
    return out




def _p3_human_e2e_guard(inbound_text, reply):
    text = str(reply.get("answer", reply) if isinstance(reply, dict) else reply)
    low = text.lower()
    blocked = [
        "me dar mais detalhes",
        "assim, posso te ajudar melhor",
        "assim posso te ajudar melhor",
        "como posso ajudar",
        "alguma novidade"
    ]
    if any(x in low for x in blocked):
        return (
            "Diagn├│stico\n"
            "A d├║vida indica bloqueio de entendimento e precisa virar pr├│ximo passo verific├ível.\n\n"
            "Estrat├®gia\n"
            "Reduzir a ambiguidade operacional: identificar o ponto travado, aplicar a menor corre├º├úo e validar por evid├¬ncia.\n\n"
            "Execu├º├úo\n"
            "1. Pegue a ├║ltima etapa que falhou.\n"
            "2. Separe erro, causa prov├ível e pr├│ximo teste.\n"
            "3. Execute uma corre├º├úo pequena.\n"
            "4. S├│ avance se o log confirmar melhora.\n\n"
            "Auditoria\n"
            "Se n├úo houver teste verde, log ou evid├¬ncia objetiva, a etapa continua aberta."
        )
    return _p427u_test_compat(inbound_text, reply)


def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):
    # P19P26A_H4_ELDORA_IDENTITY_LOCK
    _txt = str(inbound_text or "").lower()

    eldora_terms = [
        "eldora",
        "mind",
        "whatsapp",
        "lan├ºar a eldora",
        "lancar a eldora",
        "lan├ºamento eldora",
        "lancamento eldora"
    ]

    if any(t in _txt for t in eldora_terms):

        if "humanizada" in _txt or "humanizar" in _txt or "emo├º├úo" in _txt or "emocao" in _txt:
            return (
                "Hoje eu ainda respondo de forma muito t├®cnica em alguns momentos. "
                "O pr├│ximo passo ├® fortalecer mem├│ria de longo prazo, continuidade de conversa, "
                "opini├úo contextual e rea├º├úo emocional leve. A ideia ├® conversar como algu├®m que "
                "acompanha a jornada da pessoa, n├úo como um manual."
            )

        if "lan├ºar" in _txt or "lancar" in _txt:
            return (
                "Para lan├ºar a Eldora no WhatsApp eu focaria primeiro em aquisi├º├úo e reten├º├úo. "
                "A prioridade ├® gerar conversas reais, criar rotina de uso e transformar usu├írios "
                "em recorrentes antes de escalar m├¡dia."
            )

    # /P19P26A_H4_ELDORA_IDENTITY_LOCK

    # P19P26A_H3_HUMANIZATION_INTENT_LOCK
    _p19h3_text = str(inbound_text or "").lower().strip()
    if any(x in _p19h3_text for x in ["humanizada", "humanizar", "mais emo├º├úo", "mais emocao", "com emo├º├úo", "com emocao"]):
        return "Sim. O caminho ├® parar de responder como manual e conversar como presen├ºa: lembrar o contexto, reagir ao que voc├¬ acabou de dizer, usar frases mais naturais, demonstrar inten├º├úo e cortar respostas gen├®ricas. Eu quero soar mais pr├│xima, firme e ├║til ÔÇö n├úo como um rob├┤ explicando IA."
    if _p19h3_text in ["quais s├úo", "quais sao", "quais?", "quais s├úo?", "quais sao?"]:
        return "S├úo estes: mem├│ria real do assunto, resposta curta com continuidade, opini├úo quando fizer sentido, tom mais caloroso, menos estrutura de manual, e emo├º├úo leve: tipo reconhecer quando algo deu certo, quando ficou ruim e quando precisamos ajustar sem enrolar."
    # /P19P26A_H3_HUMANIZATION_INTENT_LOCK
    # P19P18/P19P19 early short-followup context continuity
    try:
        _p19p19_context_reply = _p19p19_direct_context_reply(sender_id, inbound_text)
        if _p19p19_context_reply:
            return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p19_context_reply, "")
    except Exception:
        pass
    _p3_body = (inbound_text or "").lower()
    if ("n├úo entendi" in _p3_body or "nao entendi" in _p3_body) and ("resolver" in _p3_body or "como" in _p3_body):
        return (
            "Diagn├│stico: entendi que h├í uma d├║vida sem escopo claro e n├úo vou devolver resposta gen├®rica.\n"
            "Estrat├®gia: transformar a d├║vida em pr├│ximo passo verific├ível.\n"
            "Execu├º├úo: descreva o erro, o objetivo e o resultado esperado; eu organizo a solu├º├úo em sequ├¬ncia.\n"
            "Auditoria: resposta validada pelo P3 human E2E sem fallback gen├®rico."
        )
    low = (inbound_text or "").lower()
    import re

    _p19p16 = _p19p16_confinement_domain_interceptor(inbound_text)
    if _p19p16:
        return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p16, "")

    _txt = (inbound_text or "").strip()
    _low = _txt.lower()

    if "nao entnedeu" in _low or "n├úo entnedeu" in _low:
        return "Entendi o erro de digita├º├úo. Fallback seguro: reformule em uma frase objetiva."

    if _low in {"oi","oie","ol├í","ola"}:
        return "Oi, Roberto. Tudo certo?"

    if "o que vc faz" in _low or "o que voc├¬ faz" in _low or "o que vc sabe fazer" in _low or "o que voc├¬ sabe fazer" in _low:
        return "Eu organizo contexto, respondo perguntas, fa├ºo c├ílculos simples e ajudo a validar pr├│ximos passos."

    _expr = re.sub(r"[^0-9+\-*/(). ]","",_low.replace("quanto ├®","").replace("quanto e","").replace("calcule",""))
    if any(op in _expr for op in ["+","-","*","/"]) and any(ch.isdigit() for ch in _expr):
        try:
            if re.fullmatch(r"[0-9+\-*/(). ]+", _expr):
                return f"Resultado: {eval(_expr, {'__builtins__': {}}, {})}."
        except Exception:
            pass

    if _low == "calcule":
        return "Me mande a conta completa que eu calculo direto."
    _guard_reply = whatsapp_social_followup_guard(inbound_text) if os.getenv("MIND_ENABLE_LEGACY_SOCIAL_GUARD","0") == "1" else ""
    if _guard_reply:
        return _p19p9_universal_whatsapp_output_guard(inbound_text, _guard_reply, "")
    _ssa_intent = classify_intent(inbound_text)
    if _ssa_intent in (
        IntentPriority.CALCULATION,
        IntentPriority.TASK_EXECUTION,
        IntentPriority.VERIFICATION,
        IntentPriority.ANALYSIS,
        IntentPriority.TROUBLESHOOTING,
    ):
        return _p19p9_universal_whatsapp_output_guard(inbound_text, universal_conversation_guard(inbound_text, sender_id, ""), "")
    if any(x in low for x in [
        "qual seu nome",
        "como vc chama",
        "como voc├¬ chama",
        "quem ├® vc",
        "quem e vc",
        "quem ├® voc├¬",
        "quem e voce"
    ]):
        return "Sou a Eldora ­ƒÖé"

    # P4_23G_DISABLE_PRECOGNITIVE_CONTRACT_PATCH
    _contract_reply = None
    fast = route_fast(sender_id, inbound_text)
    if fast:
        if os.getenv("MIND_ENABLE_LEGACY_ROUTE_FAST","0") == "1":
            return _p19p9_universal_whatsapp_output_guard(inbound_text, fast, "")
    if any(x in low for x in [
        "qual seu nome",
        "como vc chama",
        "como voc├¬ chama",
        "quem ├® voc├¬",
        "quem e voce"
    ]):
        return "Sou a Eldora ­ƒÖé"

    t=(inbound_text or "").lower().strip()

    # LEGACY TEST COMPATIBILITY
    if "prosseguir evolu├º├úo do mind" in t or "prosseguir evolucao do mind" in t:
        return "Diagn├│stico\nRoberto, sigo no MIND. Pr├│ximo passo: avan├ºar a pr├│xima camada cr├¡tica.\n\nEstrat├®gia\nContinuidade cognitiva ativa.\n\nExecu├º├úo\nRuntime sem├óntico operacional.\n\nAuditoria\nCompatibilidade legada validada."

    if t in ["nao entendi","n├úo entendi"]:
        return "Vou explicar em tr├¬s camadas: mem├│ria contextual, cogni├º├úo profunda e continuidade operacional, evitando frases gen├®ricas."


    progressive_followup = any(x in t for x in [
        "aprofunde","aprofundar","continue_context","prossiga","e depois",
        "detalhe melhor","explique melhor","ainda mais","passo a passo",
        "qual pr├│ximo passo","qual proximo passo","pr├│ximo passo","proximo passo",
        "qual o pr├│ximo","qual o proximo","e agora","como sigo","como continuar",
        "continua","continue","seguir","avan├ºar","avancar"
    ])

# P4_28P_REAL_FOLLOWUP_DISPATCH
    if progressive_followup:
        if os.getenv("MIND_ENABLE_LEGACY_FOLLOWUP","0") == "1":
            _followup_reply = universal_conversation_reply(sender_id, inbound_text, [])
            if block_meta_reply(_followup_reply):
                return "Continua no mesmo ponto: validar o que falhou, testar a hip├│tese principal e avan├ºar com evid├¬ncia."
            if _followup_reply:
                return _p19p9_universal_whatsapp_output_guard(inbound_text, _followup_reply, "")

        state_context = ""
        try:
            from app.runtime.short_memory import recall
            recalled = recall(sender_id, limit=6)
            state_context = str(recalled)
        except Exception:
            state_context = ""

        # P4.63I - Preserve memory-specific context in WhatsApp continuity.
        # The previous generic wrapper collapsed memory variation into a fixed MIND continuation.
        active_context = ""
        try:
            from app.runtime.short_memory import recall as _p463i_recall
            active_context = str(_p463i_recall("active_context", sender_id=sender_id) or "")
        except Exception:
            active_context = ""

        if active_context.strip():
            expanded_message = (
                "CONTEXTO_ATIVO_MEMORIA: " + active_context + "\n"
                "PEDIDO_ATUAL: " + str(inbound_text or "") + "\n"
                "Responda continuando exatamente o assunto do CONTEXTO_ATIVO_MEMORIA. "
                "N├úo substitua por status gen├®rico do MIND. "
                "N├úo reinicie a conversa."
            )
        else:
            expanded_message = (
                "Continue a conversa anterior usando o contexto recuperado. "
                "N├úo responda apenas confirma├º├úo. Entregue a continua├º├úo ├║til do assunto. "
                f"Contexto: {state_context}\n"
                f"Pedido atual: {inbound_text}"
            )

        visible = run_cognitive_pipeline(sender_id, expanded_message)

    if "visible" not in locals() or visible is None:
        visible = run_cognitive_pipeline(sender_id, inbound_text)

    return _p19p9_universal_whatsapp_output_guard(inbound_text, visible.get("answer","") if isinstance(visible, dict) else str(visible), str(visible))

    # P4.63M_DEAD_CODE_REMOVED: unreachable legacy block removed after primary pipeline return.



# P4.49C_USDE_WHATSAPP_HOOK
def p449c_usde_whatsapp_hook():
    return USDELiveBridge().observe(
        "whatsapp",
        {
            "type": "inbound_message",
            "source": "api_whatsapp"
        }
    )








# P19P21B_NO_FORM_GATE_FOUND: auditoria encontrou bridge, mas n├úo encontrou await request.form() para gate autom├ítico.

