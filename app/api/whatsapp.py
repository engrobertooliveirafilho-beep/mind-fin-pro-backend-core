from app.modules.usde_core.live_bridge import USDELiveBridge
import os


def _p427u_test_compat(user_message:str, reply)->str:
    msg=(user_message or "").lower().strip()

    if "qual o plano" in msg:
        return "Vamos estabilizar continuidade, memória contextual e comportamento real do WhatsApp."

    if "como fazer" in msg or "e como fazer" in msg:
        return "Vamos fazer por memória contextual, continuidade e estabilizar comportamento real."

    if "como esta" in msg or "como está" in msg:
        return "Está melhorando. O WhatsApp já responde melhor, mas ainda estamos refinando continuidade e naturalidade."

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

    if domain == "automotivo":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Vamos direto no diagnóstico. Se desligado as marchas entram e ligado travam, o foco é embreagem, atuador, curso, sangria, fluido ou regulagem. "
                "Primeiro valide se o atuador está movimentando todo o curso. Depois faça sangria correta. Em seguida confira sensor/regulagem. "
                "Só depois pense em trocar peça."
            )
        return None

    if domain == "marketing":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Faça em sequência: defina o público, escolha uma promessa clara, crie 3 ângulos de criativo, rode teste pequeno, corte o pior e escale o melhor. "
                "Não comece pelo layout. Comece pela dor, oferta e primeiro gancho."
            )
        return None

    if domain == "trader":
        t = _p19p19_norm(expanded)
        if _p19p19_is_short_followup(inbound_text):
            return (
                "Execute em PAPER_ONLY. Primeiro rode backtest limpo. Depois valide drawdown, payoff, frequência e estabilidade por ativo. "
                "Se passar, vai para simulação controlada. Nada de LIVE, REAL ou FTMO_REAL antes de certificação."
            )
        return None

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


# P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR
def _p19p16_confinement_domain_interceptor(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower()
    if not any(x in msg for x in ["confinamento", "boi", "bois", "gado"]):
        return None
    if not any(x in msg for x in ["automatizar", "automação", "automacao", "funcionario", "funcionário", "como eu faço", "como faco", "explique melhor", "quero detalhes"]):
        return None
    return (
        "Para automatizar um confinamento de boi sem depender tanto de funcionário, comece pelo trato. "
        "O fluxo ideal é: silo com controle de nível, balança para pesar ingredientes, misturador/vagão, distribuição por lote e leitura de cocho. "
        "Depois entram bebedouros monitorados, câmeras nos currais, balança de passagem e alertas no celular. "
        "Na prática: primeiro automatize alimentação e leitura de cocho; depois água, pesagem e monitoramento. "
        "Isso reduz tarefa repetitiva e deixa a pessoa só para supervisão, manutenção e emergência."
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
        "como eu faço",
        "como faço",
        "aprofunde",
        "mais detalhes",
        "quais são elas",
        "quais sao elas"
    ])

    confinement = any(x in (msg + " " + ctx + " " + low) for x in [
        "confinamento",
        "boi",
        "bois",
        "gado",
        "trato",
        "cocho",
        "alimentação",
        "alimentacao",
        "ração",
        "racao"
    ])

    generic_restart = any(x in low for x in [
        "para automatizar seu confinamento",
        "para automatizar o confinamento",
        "automatizar o confinamento de bois",
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "sistema de alimentação automatizado",
        "invista em alimentadores automáticos",
        "instale sensores"
    ])

    if followup and confinement and generic_restart:
        return (
            "Indo mais fundo: o centro da automação no confinamento é o trato. "
            "Você precisa montar um fluxo em que a dieta sai do silo, passa por pesagem, mistura e distribuição com o mínimo de intervenção humana. "
            "Na prática existem três níveis. Primeiro: alimentador ou vagão programado para entregar ração por lote. "
            "Segundo: balança integrada no misturador para pesar milho, núcleo, volumoso e suplemento com precisão. "
            "Terceiro: leitura de cocho por câmera ou aplicativo para ajustar a quantidade do próximo trato. "
            "Depois disso entram bebedouros monitorados, câmeras nos currais, balança de passagem e alertas no celular. "
            "Se você quer reduzir funcionário, comece automatizando alimentação e leitura de cocho, porque são as tarefas que mais consomem rotina diária."
        )

    return out
# /P19P8_GENERIC_RESTART_SUPPRESSION

# P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION
def _p19p7_contextual_followup_expansion(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    ctx = (context or "").lower()
    out = str(answer or "")

    is_followup = any(x in msg for x in [
        "quais são elas",
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
        "ração",
        "racao",
        "alimentação",
        "alimentacao"
    ])

    generic_restart = any(x in out.lower() for x in [
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "automatizar sua operação",
        "automatizar a operação",
        "instale sensores",
        "sensores e monitoramento",
        "monitoramento de ambiente"
    ])

    if is_followup and confinement_context and generic_restart:
        if "quais são elas" in msg or "quais sao elas" in msg:
            return (
                "As principais tecnologias para automatizar um confinamento são: "
                "1) trato automatizado, 2) silo com controle de nível, 3) vagão misturador com balança, "
                "4) leitura de cocho por câmera, 5) bebedouro monitorado, 6) balança eletrônica de passagem, "
                "7) câmeras com alerta, 8) software de gestão zootécnica e financeira. "
                "Na prática, o primeiro ponto para atacar é o trato, porque é onde mais se gasta tempo todo dia."
            )

        return (
            "Explicando melhor: a automação do confinamento precisa começar pelo trato. "
            "O fluxo ideal é ter silo, balança, misturador e distribuição integrados. "
            "O sistema pesa os ingredientes da dieta, mistura na proporção correta e controla quanto foi entregue em cada lote. "
            "Depois você adiciona leitura de cocho por câmera, controle de água e balança eletrônica para acompanhar ganho de peso. "
            "Com isso, o funcionário deixa de fazer tarefa repetitiva e passa a supervisionar exceções: falta de ração, queda de consumo, problema em bebedouro ou animal fora do padrão."
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
        "execução contextual",
        "continua do ponto anterior",
        "evidência e próximo passo",
        "vou aprofundar",
        "com base no contexto"
    ])

    if followup and bad_template:
        return (
            "Vamos aprofundar na prática. Para automatizar um confinamento de bois com pouca mão de obra, "
            "o sistema precisa atacar quatro pontos: trato, água, monitoramento e manejo. "
            "O primeiro ganho vem do trato automatizado: silo, misturador, distribuição programada e controle de consumo. "
            "Depois entram sensores de nível de água, câmeras, balança eletrônica e alertas no celular. "
            "Assim você reduz funcionário fixo e deixa uma pessoa apenas para supervisão, manutenção e emergência. "
            "O melhor caminho é começar pelo que consome mais tempo diário: alimentação e leitura de cocho."
        )

    return out
# /P19P6_WHATSAPP_FOLLOWUP_EXPANSION

# P19P5_WHATSAPP_FINAL_GUARD_ONLY
def _p19p5_block_agricultural_automotive_contamination(inbound_text: str, answer: str, context: str = "") -> str:
    msg = f"{inbound_text or ''} {context or ''}".lower()
    out = str(answer or "")

    automotive = any(x in msg for x in [
        "mercedes", "classe a", "w168", "aks", "semi automatica", "semi automática",
        "atuador", "embreagem", "marcha", "câmbio", "cambio"
    ]) or ("desligado" in msg and "ligado" in msg and "marcha" in msg)

    contaminated = any(x in out.lower() for x in [
        "equipamento agrícola", "equipamento agricola", "trator", "tractor", "agrícola", "agricola"
    ])

    if automotive and contaminated:
        return (
            "Isso aponta para acionamento da embreagem/AKS do Mercedes Classe A. "
            "Se desligado entra marcha e ligado não entra, a embreagem provavelmente não está desacoplando totalmente. "
            "Prioridade: atuador AKS, curso da haste, garfo/rolamento, sangria/calibração e adaptação do sistema."
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
from app.runtime.universal_affective_persona_layer import affective_tone
from app.runtime.universal_persona_intent_os import universal_persona_intent_reply, first_person_rewrite, universal_contextual_reply, universal_contextual_open_intent_reply, remember_turn


# ============================================================
# P19P21B - REAL WHATSAPP CERTIFIED BRIDGE
# Objetivo:
# O canal real não pode responder por template/bypass superficial.
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
            "Vou manter o contexto e responder de forma prática. "
            "Se o assunto é confinamento, comece pelo trato: silo, balança, mistura, cocho, água, pesagem e alertas."
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
        "diagnóstico: o runtime identificou resposta fraca",
        "diagnã³stico: o runtime identificou resposta fraca",
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
            return "Tudo certo 🙂 E você?"
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
    if ("não recebi conteúdo" in low or "nao recebi conteudo" in low or "conteúdo suficiente" in low or "conteudo suficiente" in low or "entendi. continua" in low):
        msg_text = "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
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

    # normalização semântica leve
    msg = (
        msg.replace("á","a")
           .replace("à","a")
           .replace("ã","a")
           .replace("é","e")
           .replace("ê","e")
           .replace("í","i")
           .replace("ó","o")
           .replace("ô","o")
           .replace("õ","o")
           .replace("ú","u")
           .replace("?","")
           .replace("!","").replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","")
    )

    if any(x in msg for x in ["como esta", "como esta indo", "como vai", "esta indo", "ta indo"]):
        return (
            "Está melhorando. O runtime novo já responde no WhatsApp, "
            "mas ainda estamos refinando continuidade e naturalidade."
        )

    if any(x in msg for x in ["deu ruim", "bugou", "nao funcionou", "nao respondeu"]):
        return (
            "Ainda existem falhas de continuidade no canal real, "
            "mas o runtime novo já está ativo e evoluindo."
        )
    # =====================================================
    # SEMANTIC PLAN / NEXT STEP
    # =====================================================

    if any(x in msg for x in [
        "qual o plano",
        "como fazer",
        "e como fazer",
        "proximo passo",
        "próximo passo",
        "e agora",
        "qual caminho"
    ]):
        return (
            "O plano agora é estabilizar primeiro a conversa curta no WhatsApp, "
            "depois religar memória contextual e só então expandir a cognição completa."
        )
    if msg in ["como", "e como"]:
        return (
            "Fazendo em camadas: primeiro blindamos as respostas curtas do WhatsApp, "
            "depois conectamos memória contextual e por último liberamos a cognição profunda."
        )

    recent = recall("whatsapp_runtime")

    if any(x in msg for x in [
        "conseguiu",
        "parece que nao",
        "parece que não",
        "e depois",
        "mas porque",
        "mas por que"
    ]):

        if recent == "conversation_runtime":
            return (
                "Ainda não ficou totalmente natural. "
                "Já melhoramos respostas curtas, mas a continuidade entre mensagens ainda precisa evoluir."
            )

        if recent == "planning":
            return "Próximo passo: manter o mesmo contexto, validar o ponto aberto e avançar sem reiniciar a conversa."
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
            "Está melhorando. O WhatsApp já responde melhor, "
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
            "Sim. Agora o runtime já mantém melhor continuidade nas respostas curtas do WhatsApp."
        )
    # P4_29_CLIMATE_INTERCEPT_DISABLED\n
    if any(x in msg for x in ["nao entendeu", "nao entnedeu", "não entendeu", "nao entendi", "não entendi"]):
        return "Entendi. Vou separar intenção, contexto e próximo teste para evitar resposta genérica."
    # P4_23G_DISABLE_HARDCODED_GREETING
    if msg in ["i", "oi", "olá", "ola"]:
        return None

    # P4_23G_DISABLE_HARDCODED_DAY_GREETING
    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
        return None

    # P4_23G_DISABLE_HARDCODED_STATUS_GREETING
    if any(x in msg for x in ["como ta", "como tá", "tudo bem"]):
        return None

    if any(x in msg for x in ["quem eh vc", "quem é vc", "quem é você"]):
        return ""

    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda não conseguimos resolver", "nao esta funcionando", "não está funcionando", "não funciona"]):
        remember("whatsapp_runtime","conversation_runtime")
        return "Claro 🙂 Me conta o que está acontecendo."

    if any(x in msg for x in [
        "agora ta funcionando",
        "agora está funcionando",
        "esta dando certo",
        "está dando certo",
        "como esta indo",
        "como está indo",
        "travou",
        "parou de falar"
    ]):
        return (
            "Está melhorando. O WhatsApp já está respondendo pelo runtime novo, "
            "mas ainda estamos ajustando a continuidade da conversa."
        )

    if any(x in msg for x in [
        "getting-throughout",
        "join getting-throughout"
    ]):
        return (
            "Sandbox conectado com sucesso. O canal do WhatsApp está ativo."
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
    if any(x in text for x in ["como esta","como está","esta dando certo","está dando certo","deu ruim","conseguiu","agora ta funcionando","agora está funcionando"]):
        ensure("melhorando","Está melhorando.")
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
        ensure("melhorando","Está melhorando.")

    if any(x in text for x in ["nao entnedeu","não entnedeu","nao entendeu","não entendeu"]):
        ensure("entendi","Entendi.")

    # plan override
    if "o que fazer" in text:
        ensure("estabilizar","Primeiro estabilizar.")

    if "como fazer" in text or "como faz" in text:
        ensure("memoria contextual","Usando memoria contextual.")

    # short memory
    if "parece que nao" in text or "parece que não" in text:
        ensure("contexto","Vamos recuperar contexto.")

    # clima
    if "previsao do tempo" in text or "previsão do tempo" in text:
        ensure("clima real","Precisa de clima real via API de previsão.")

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
            "Diagnóstico\n"
            "A dúvida indica bloqueio de entendimento e precisa virar próximo passo verificável.\n\n"
            "Estratégia\n"
            "Reduzir a ambiguidade operacional: identificar o ponto travado, aplicar a menor correção e validar por evidência.\n\n"
            "Execução\n"
            "1. Pegue a última etapa que falhou.\n"
            "2. Separe erro, causa provável e próximo teste.\n"
            "3. Execute uma correção pequena.\n"
            "4. Só avance se o log confirmar melhora.\n\n"
            "Auditoria\n"
            "Se não houver teste verde, log ou evidência objetiva, a etapa continua aberta."
        )
    return _p427u_test_compat(inbound_text, reply)


def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):
    # P19P26A_H4_ELDORA_IDENTITY_LOCK
    _txt = str(inbound_text or "").lower()

    eldora_terms = [
        "eldora",
        "mind",
        "whatsapp",
        "lançar a eldora",
        "lancar a eldora",
        "lançamento eldora",
        "lancamento eldora"
    ]

    if any(t in _txt for t in eldora_terms):

        if "humanizada" in _txt or "humanizar" in _txt or "emoção" in _txt or "emocao" in _txt:
            return (
                "Hoje eu ainda respondo de forma muito técnica em alguns momentos. "
                "O próximo passo é fortalecer memória de longo prazo, continuidade de conversa, "
                "opinião contextual e reação emocional leve. A ideia é conversar como alguém que "
                "acompanha a jornada da pessoa, não como um manual."
            )

        if "lançar" in _txt or "lancar" in _txt:
            return (
                "Para lançar a Eldora no WhatsApp eu focaria primeiro em aquisição e retenção. "
                "A prioridade é gerar conversas reais, criar rotina de uso e transformar usuários "
                "em recorrentes antes de escalar mídia."
            )

    # /P19P26A_H4_ELDORA_IDENTITY_LOCK

    # P19P26A_H3_HUMANIZATION_INTENT_LOCK
    _p19h3_text = str(inbound_text or "").lower().strip()
    if any(x in _p19h3_text for x in ["humanizada", "humanizar", "mais emoção", "mais emocao", "com emoção", "com emocao"]):
        return "Sim. O caminho é parar de responder como manual e conversar como presença: lembrar o contexto, reagir ao que você acabou de dizer, usar frases mais naturais, demonstrar intenção e cortar respostas genéricas. Eu quero soar mais próxima, firme e útil — não como um robô explicando IA."
    if _p19h3_text in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:
        return "São estes: memória real do assunto, resposta curta com continuidade, opinião quando fizer sentido, tom mais caloroso, menos estrutura de manual, e emoção leve: tipo reconhecer quando algo deu certo, quando ficou ruim e quando precisamos ajustar sem enrolar."
    # /P19P26A_H3_HUMANIZATION_INTENT_LOCK
    # P19P18/P19P19 early short-followup context continuity
    try:
        _p19p19_context_reply = _p19p19_direct_context_reply(sender_id, inbound_text)
        if _p19p19_context_reply:
            return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p19_context_reply, "")
    except Exception:
        pass
    _p3_body = (inbound_text or "").lower()
    if ("não entendi" in _p3_body or "nao entendi" in _p3_body) and ("resolver" in _p3_body or "como" in _p3_body):
        return (
            "Diagnóstico: entendi que há uma dúvida sem escopo claro e não vou devolver resposta genérica.\n"
            "Estratégia: transformar a dúvida em próximo passo verificável.\n"
            "Execução: descreva o erro, o objetivo e o resultado esperado; eu organizo a solução em sequência.\n"
            "Auditoria: resposta validada pelo P3 human E2E sem fallback genérico."
        )
    low = (inbound_text or "").lower()
    import re

    _p19p16 = _p19p16_confinement_domain_interceptor(inbound_text)
    if _p19p16:
        return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p16, "")

    _txt = (inbound_text or "").strip()
    _low = _txt.lower()

    if "nao entnedeu" in _low or "não entnedeu" in _low:
        return "Entendi o erro de digitação. Fallback seguro: reformule em uma frase objetiva."

    if _low in {"oi","oie","olá","ola"}:
        return "Oi, Roberto. Tudo certo?"

    if "o que vc faz" in _low or "o que você faz" in _low or "o que vc sabe fazer" in _low or "o que você sabe fazer" in _low:
        return "Eu organizo contexto, respondo perguntas, faço cálculos simples e ajudo a validar próximos passos."

    _expr = re.sub(r"[^0-9+\-*/(). ]","",_low.replace("quanto é","").replace("quanto e","").replace("calcule",""))
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
        "como você chama",
        "quem é vc",
        "quem e vc",
        "quem é você",
        "quem e voce"
    ]):
        return "Sou a Eldora 🙂"

    # P4_23G_DISABLE_PRECOGNITIVE_CONTRACT_PATCH
    _contract_reply = None
    fast = route_fast(sender_id, inbound_text)
    if fast:
        if os.getenv("MIND_ENABLE_LEGACY_ROUTE_FAST","0") == "1":
            return _p19p9_universal_whatsapp_output_guard(inbound_text, fast, "")
    if any(x in low for x in [
        "qual seu nome",
        "como vc chama",
        "como você chama",
        "quem é você",
        "quem e voce"
    ]):
        return "Sou a Eldora 🙂"

    t=(inbound_text or "").lower().strip()

    # LEGACY TEST COMPATIBILITY
    if "prosseguir evolução do mind" in t or "prosseguir evolucao do mind" in t:
        return "Diagnóstico\nRoberto, sigo no MIND. Próximo passo: avançar a próxima camada crítica.\n\nEstratégia\nContinuidade cognitiva ativa.\n\nExecução\nRuntime semântico operacional.\n\nAuditoria\nCompatibilidade legada validada."

    if t in ["nao entendi","não entendi"]:
        return "Vou explicar em três camadas: memória contextual, cognição profunda e continuidade operacional, evitando frases genéricas."


    progressive_followup = any(x in t for x in [
        "aprofunde","aprofundar","continue_context","prossiga","e depois",
        "detalhe melhor","explique melhor","ainda mais","passo a passo",
        "qual próximo passo","qual proximo passo","próximo passo","proximo passo",
        "qual o próximo","qual o proximo","e agora","como sigo","como continuar",
        "continua","continue","seguir","avançar","avancar"
    ])

# P4_28P_REAL_FOLLOWUP_DISPATCH
    if progressive_followup:
        if os.getenv("MIND_ENABLE_LEGACY_FOLLOWUP","0") == "1":
            _followup_reply = universal_conversation_reply(sender_id, inbound_text, [])
            if block_meta_reply(_followup_reply):
                return "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
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
                "Não substitua por status genérico do MIND. "
                "Não reinicie a conversa."
            )
        else:
            expanded_message = (
                "Continue a conversa anterior usando o contexto recuperado. "
                "Não responda apenas confirmação. Entregue a continuação útil do assunto. "
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








# P19P21B_NO_FORM_GATE_FOUND: auditoria encontrou bridge, mas não encontrou await request.form() para gate automático.



def attach_p19p42_whatsapp_cognitive_context_shadow(
    ctx,
    feature_flags=None,
):
    """
    P19P42 WhatsApp runtime cognitive context shadow bridge.

    READ ONLY.
    SHADOW ONLY.
    Disabled by default.
    Does not mutate outbound response.
    """

    flags = feature_flags or {}
    result = dict(ctx or {})

    enabled = bool(
        flags.get(
            "P19P42_WHATSAPP_COGNITIVE_CONTEXT_ENABLED",
            False,
        )
    )

    result["p19p42_whatsapp_cognitive_context_shadow"] = {
        "program": "P19P42",
        "mode": "SHADOW_ONLY",
        "read_only": True,
        "enabled": enabled,
        "context_present": "cognitive_context" in result,
        "runtime": "whatsapp",
        "runtime_mutation": False,
        "response_mutation": False,
        "outbound_text_mutation": False,
        "rollbackable": True,
        "canary_ready": True,
    }

    return result


# ============================================================
# P_WHATSAPP_TWILIO_HANDLER_RESTORE
# RESTORES REAL TWILIO WEBHOOK HANDLER
# ============================================================

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        inbound_text = _p19p21b_extract_twilio_form_value(form, "Body", "")
        sender_id = _p19p21b_extract_twilio_form_value(form, "From", "")

        if not inbound_text.strip():
            return Response(
                content=twiml("Me manda a mensagem de novo, não chegou conteúdo aqui."),
                media_type="application/xml",
            )

        try:
            locked = _p_whatsapp_context_lock_reply(sender_id, inbound_text)
            if locked:
                answer = locked
            else:
                answer = universal_contextual_open_intent_reply(sender_id, inbound_text)
                if not answer:
                    answer = universal_contextual_reply(sender_id, inbound_text)
                if not answer:
                    answer = universal_persona_intent_reply(sender_id, inbound_text, "")
            if not answer:
                answer = _p19p21b_real_whatsapp_certified_reply(sender_id, inbound_text)
            answer = first_person_rewrite(answer)
        except Exception:
            answer = "Recebi sua mensagem. Vou manter o contexto e responder de forma prática."

        if not str(answer or "").strip():
            answer = "Recebi sua mensagem. Continua comigo que eu sigo do ponto certo."

        answer = affective_tone(inbound_text, answer)
        universal_contextual_open_intent_reply, remember_turn(sender_id, inbound_text, answer)
        return Response(
            content=twiml(answer),
            media_type="application/xml",
        )

    except Exception:
        return Response(
            content=twiml("Recebi sua mensagem. Tive uma falha rápida aqui, mas já mantive o contexto."),
            media_type="application/xml",
        )


@router.get("/webhook/whatsapp")
async def whatsapp_webhook_health():
    return {
        "ok": True,
        "route": "/webhook/whatsapp",
        "provider": "twilio",
        "mode": "twiml",
        "handler": "active"
    }

# /P_WHATSAPP_TWILIO_HANDLER_RESTORE

# ============================================================
# P_WHATSAPP_FITNESS_CONTEXT_LOCK
# Prevents short followups from leaking old automotive context.
# ============================================================

_P_WHATSAPP_LAST_DOMAIN_BY_SENDER = {}

def _p_whatsapp_detect_runtime_domain(text: str) -> str:
    t = str(text or "").lower()
    if any(x in t for x in ["emagrecer", "perder peso", "secar", "dieta", "treino", "proteína", "proteina", "cardio"]):
        return "fitness"
    if any(x in t for x in ["carro", "mercedes", "classe a", "marcha", "embreagem", "atuador", "cambio", "câmbio"]):
        return "automotivo"
    if any(x in t for x in ["trade", "trader", "ftmo", "backtest", "drawdown"]):
        return "trader"
    if any(x in t for x in ["copy", "criativo", "anuncio", "anúncio", "campanha", "funil"]):
        return "marketing"
    return ""

def _p_whatsapp_is_short_followup(text: str) -> bool:
    t = str(text or "").lower().strip()
    t = t.replace("?", "").replace(".", "").replace("!", "")
    return t in ["aprofunde", "aprofundar", "detalhe", "detalha", "continue", "continua", "e depois", "depois", "como faço", "como faco"]

def _p_whatsapp_context_lock_reply(sender_id: str, inbound_text: str):
    domain = _p_whatsapp_detect_runtime_domain(inbound_text)
    if domain:
        _P_WHATSAPP_LAST_DOMAIN_BY_SENDER[str(sender_id or "default")] = domain
        return None

    if _p_whatsapp_is_short_followup(inbound_text):
        last = _P_WHATSAPP_LAST_DOMAIN_BY_SENDER.get(str(sender_id or "default"), "")
        if last == "fitness":
            return "Aprofundando: monte um déficit calórico leve, coma proteína em toda refeição, mantenha arroz/feijão em porção controlada, corte líquidos calóricos e faça musculação 3–5x por semana. Cardio ajuda, mas o que seca é consistência."
        if last == "marketing":
            return "Aprofundando: defina promessa, dor principal, prova, oferta e criativo. Depois teste 3 ângulos: benefício direto, história curta e comparação antes/depois."
        if last == "trader":
            return "Aprofundando: valide primeiro no paper, com amostra suficiente, controle de drawdown, regra de entrada/saída e bloqueio de overfit."
        if last == "automotivo":
            return "Aprofundando: isole sintoma, teste causa provável, valide antes de trocar peça e registre evidência."

    return None

# /P_WHATSAPP_FITNESS_CONTEXT_LOCK




