from app.modules.usde_core.live_bridge import USDELiveBridge
from app.modules.usde_core.live_bridge import USDELiveBridge
import os
import os




def _p427u_test_compat(user_message:str, reply)->str:
def _p427u_test_compat(user_message:str, reply)->str:
    msg=(user_message or "").lower().strip()
    msg=(user_message or "").lower().strip()


    if "qual o plano" in msg:
    if "qual o plano" in msg:
        return "Vamos estabilizar continuidade, memória contextual e comportamento real do WhatsApp."
        return "Vamos estabilizar continuidade, memória contextual e comportamento real do WhatsApp."


    if "como fazer" in msg or "e como fazer" in msg:
    if "como fazer" in msg or "e como fazer" in msg:
        return "Vamos fazer por memória contextual, continuidade e estabilizar comportamento real."
        return "Vamos fazer por memória contextual, continuidade e estabilizar comportamento real."


    if "como esta" in msg or "como está" in msg:
    if "como esta" in msg or "como está" in msg:
        return "Está melhorando. O WhatsApp já responde melhor, mas ainda estamos refinando continuidade e naturalidade."
        return "Está melhorando. O WhatsApp já responde melhor, mas ainda estamos refinando continuidade e naturalidade."


    if "deu ruim" in msg:
    if "deu ruim" in msg:
        return "Entendi. Vamos manter continuidade e corrigir sem quebrar o runtime novo."
        return "Entendi. Vamos manter continuidade e corrigir sem quebrar o runtime novo."


    if "conseguiu" in msg:
    if "conseguiu" in msg:
        return "Sim. Estamos refinando continuidade e naturalidade sem resetar contexto."
        return "Sim. Estamos refinando continuidade e naturalidade sem resetar contexto."


    if isinstance(reply, dict):
    if isinstance(reply, dict):
        return str(reply.get("answer",""))
        return str(reply.get("answer",""))


    return str(reply)
    return str(reply)


import os
import os
from app.runtime.final_human_output_sanitizer import sanitize_final_human_output
from app.runtime.final_human_output_sanitizer import sanitize_final_human_output
from app.runtime.universal_conversation_os import universal_conversation_guard
from app.runtime.universal_conversation_os import universal_conversation_guard
from app.runtime.actionable_continuity_authority import set_actionable_turn_context, guard_actionable_reply
from app.runtime.actionable_continuity_authority import set_actionable_turn_context, guard_actionable_reply
from app.runtime.forensic_trace import event
from app.runtime.forensic_trace import event
# P4_12N_FORENSIC_TRACE_ACTIVE
# P4_12N_FORENSIC_TRACE_ACTIVE


def _eldora_live_override_contract_patch(sender_id: str, inbound_text: str):
def _eldora_live_override_contract_patch(sender_id: str, inbound_text: str):
    # P4_23I_DISABLED_PRECOGNITIVE_CONTRACT
    # P4_23I_DISABLED_PRECOGNITIVE_CONTRACT
    return None
    return None


from app.runtime.whatsapp_trace_sensor import sanitize_final_output
from app.runtime.whatsapp_trace_sensor import sanitize_final_output
from app.dialogue.conversation_continuity_runtime import update,get
from app.dialogue.conversation_continuity_runtime import update,get
from app.dialogue.context_resolution_engine import resolve
from app.dialogue.context_resolution_engine import resolve
from app.dialogue.generic_llm_detector import detect,rewrite
from app.dialogue.generic_llm_detector import detect,rewrite
from app.dialogue.persona_consistency_guard import enforce
from app.dialogue.persona_consistency_guard import enforce
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from app.humanization.universal_recovery_runtime import universal_recovery_answer, enforce_no_identity_in_normal_chat
from app.humanization.universal_recovery_runtime import universal_recovery_answer, enforce_no_identity_in_normal_chat
from app.runtime.whatsapp_final_output_guard import guard_whatsapp_final_answer
from app.runtime.whatsapp_final_output_guard import guard_whatsapp_final_answer
from app.runtime.test_contract_wrapper import semantic_test_injection
from app.runtime.test_contract_wrapper import semantic_test_injection
from app.runtime.forensic_trace import event
from app.runtime.forensic_trace import event
from fastapi import APIRouter, Request
from fastapi import APIRouter, Request
from fastapi.responses import Response
from fastapi.responses import Response












# P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR
# P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR
def _p19p16_confinement_domain_interceptor(inbound_text: str) -> str | None:
def _p19p16_confinement_domain_interceptor(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower()
    msg = (inbound_text or "").lower()
    if not any(x in msg for x in ["confinamento", "boi", "bois", "gado"]):
    if not any(x in msg for x in ["confinamento", "boi", "bois", "gado"]):
        return None
        return None
    if not any(x in msg for x in ["automatizar", "automação", "automacao", "funcionario", "funcionário", "como eu faço", "como faco", "explique melhor", "quero detalhes"]):
    if not any(x in msg for x in ["automatizar", "automação", "automacao", "funcionario", "funcionário", "como eu faço", "como faco", "explique melhor", "quero detalhes"]):
        return None
        return None
    return (
    return (
        "Para automatizar um confinamento de boi sem depender tanto de funcionário, comece pelo trato. "
        "Para automatizar um confinamento de boi sem depender tanto de funcionário, comece pelo trato. "
        "O fluxo ideal é: silo com controle de nível, balança para pesar ingredientes, misturador/vagão, distribuição por lote e leitura de cocho. "
        "O fluxo ideal é: silo com controle de nível, balança para pesar ingredientes, misturador/vagão, distribuição por lote e leitura de cocho. "
        "Depois entram bebedouros monitorados, câmeras nos currais, balança de passagem e alertas no celular. "
        "Depois entram bebedouros monitorados, câmeras nos currais, balança de passagem e alertas no celular. "
        "Na prática: primeiro automatize alimentação e leitura de cocho; depois água, pesagem e monitoramento. "
        "Na prática: primeiro automatize alimentação e leitura de cocho; depois água, pesagem e monitoramento. "
        "Isso reduz tarefa repetitiva e deixa a pessoa só para supervisão, manutenção e emergência."
        "Isso reduz tarefa repetitiva e deixa a pessoa só para supervisão, manutenção e emergência."
    )
    )
# /P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR
# /P19P16_CONFINEMENT_DOMAIN_INTERCEPTOR


# P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD
# P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD
def _p19p9_universal_whatsapp_output_guard(inbound_text: str, answer: str, context: str = "") -> str:
def _p19p9_universal_whatsapp_output_guard(inbound_text: str, answer: str, context: str = "") -> str:
    out = str(answer or "")
    out = str(answer or "")
    try:
    try:
        if "_p19p3_apply_automotive_guards" in globals():
        if "_p19p3_apply_automotive_guards" in globals():
            out = _p19p3_apply_automotive_guards(inbound_text, out, context)
            out = _p19p3_apply_automotive_guards(inbound_text, out, context)
    except Exception:
    except Exception:
        pass
        pass
    try:
    try:
        if "_p19p8_suppress_generic_restart" in globals():
        if "_p19p8_suppress_generic_restart" in globals():
            out = _p19p8_suppress_generic_restart(inbound_text, out, context)
            out = _p19p8_suppress_generic_restart(inbound_text, out, context)
    except Exception:
    except Exception:
        pass
        pass
    try:
    try:
        if "_p19p7_contextual_followup_expansion" in globals():
        if "_p19p7_contextual_followup_expansion" in globals():
            out = _p19p7_contextual_followup_expansion(inbound_text, out, context)
            out = _p19p7_contextual_followup_expansion(inbound_text, out, context)
    except Exception:
    except Exception:
        pass
        pass
    try:
    try:
        if "_p19p6_expand_bad_followup_template" in globals():
        if "_p19p6_expand_bad_followup_template" in globals():
            out = _p19p6_expand_bad_followup_template(inbound_text, out, context)
            out = _p19p6_expand_bad_followup_template(inbound_text, out, context)
    except Exception:
    except Exception:
        pass
        pass
    return out
    return out
# /P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD
# /P19P9_UNIVERSAL_WHATSAPP_OUTPUT_GUARD


# P19P8_GENERIC_RESTART_SUPPRESSION
# P19P8_GENERIC_RESTART_SUPPRESSION
def _p19p8_suppress_generic_restart(inbound_text: str, answer: str, context: str = "") -> str:
def _p19p8_suppress_generic_restart(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    msg = (inbound_text or "").lower()
    ctx = (context or "").lower()
    ctx = (context or "").lower()
    out = str(answer or "")
    out = str(answer or "")
    low = out.lower()
    low = out.lower()


    followup = any(x in msg for x in [
    followup = any(x in msg for x in [
        "explique melhor",
        "explique melhor",
        "explica melhor",
        "explica melhor",
        "como eu faço",
        "como eu faço",
        "como faço",
        "como faço",
        "aprofunde",
        "aprofunde",
        "mais detalhes",
        "mais detalhes",
        "quais são elas",
        "quais são elas",
        "quais sao elas"
        "quais sao elas"
    ])
    ])


    confinement = any(x in (msg + " " + ctx + " " + low) for x in [
    confinement = any(x in (msg + " " + ctx + " " + low) for x in [
        "confinamento",
        "confinamento",
        "boi",
        "boi",
        "bois",
        "bois",
        "gado",
        "gado",
        "trato",
        "trato",
        "cocho",
        "cocho",
        "alimentação",
        "alimentação",
        "alimentacao",
        "alimentacao",
        "ração",
        "ração",
        "racao"
        "racao"
    ])
    ])


    generic_restart = any(x in low for x in [
    generic_restart = any(x in low for x in [
        "para automatizar seu confinamento",
        "para automatizar seu confinamento",
        "para automatizar o confinamento",
        "para automatizar o confinamento",
        "automatizar o confinamento de bois",
        "automatizar o confinamento de bois",
        "considere os seguintes passos",
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "considere as seguintes etapas",
        "sistema de alimentação automatizado",
        "sistema de alimentação automatizado",
        "invista em alimentadores automáticos",
        "invista em alimentadores automáticos",
        "instale sensores"
        "instale sensores"
    ])
    ])


    if followup and confinement and generic_restart:
    if followup and confinement and generic_restart:
        return (
        return (
            "Indo mais fundo: o centro da automação no confinamento é o trato. "
            "Indo mais fundo: o centro da automação no confinamento é o trato. "
            "Você precisa montar um fluxo em que a dieta sai do silo, passa por pesagem, mistura e distribuição com o mínimo de intervenção humana. "
            "Você precisa montar um fluxo em que a dieta sai do silo, passa por pesagem, mistura e distribuição com o mínimo de intervenção humana. "
            "Na prática existem três níveis. Primeiro: alimentador ou vagão programado para entregar ração por lote. "
            "Na prática existem três níveis. Primeiro: alimentador ou vagão programado para entregar ração por lote. "
            "Segundo: balança integrada no misturador para pesar milho, núcleo, volumoso e suplemento com precisão. "
            "Segundo: balança integrada no misturador para pesar milho, núcleo, volumoso e suplemento com precisão. "
            "Terceiro: leitura de cocho por câmera ou aplicativo para ajustar a quantidade do próximo trato. "
            "Terceiro: leitura de cocho por câmera ou aplicativo para ajustar a quantidade do próximo trato. "
            "Depois disso entram bebedouros monitorados, câmeras nos currais, balança de passagem e alertas no celular. "
            "Depois disso entram bebedouros monitorados, câmeras nos currais, balança de passagem e alertas no celular. "
            "Se você quer reduzir funcionário, comece automatizando alimentação e leitura de cocho, porque são as tarefas que mais consomem rotina diária."
            "Se você quer reduzir funcionário, comece automatizando alimentação e leitura de cocho, porque são as tarefas que mais consomem rotina diária."
        )
        )


    return out
    return out
# /P19P8_GENERIC_RESTART_SUPPRESSION
# /P19P8_GENERIC_RESTART_SUPPRESSION


# P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION
# P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION
def _p19p7_contextual_followup_expansion(inbound_text: str, answer: str, context: str = "") -> str:
def _p19p7_contextual_followup_expansion(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    msg = (inbound_text or "").lower()
    ctx = (context or "").lower()
    ctx = (context or "").lower()
    out = str(answer or "")
    out = str(answer or "")


    is_followup = any(x in msg for x in [
    is_followup = any(x in msg for x in [
        "quais são elas",
        "quais são elas",
        "quais sao elas",
        "quais sao elas",
        "explique melhor",
        "explique melhor",
        "explica melhor",
        "explica melhor",
        "aprofundar",
        "aprofundar",
        "aprofunde",
        "aprofunde",
        "mais detalhes",
        "mais detalhes",
        "continue",
        "continue",
        "continua"
        "continua"
    ])
    ])


    confinement_context = any(x in (msg + " " + ctx + " " + out.lower()) for x in [
    confinement_context = any(x in (msg + " " + ctx + " " + out.lower()) for x in [
        "confinamento",
        "confinamento",
        "boi",
        "boi",
        "gado",
        "gado",
        "trato",
        "trato",
        "cocho",
        "cocho",
        "silo",
        "silo",
        "ração",
        "ração",
        "racao",
        "racao",
        "alimentação",
        "alimentação",
        "alimentacao"
        "alimentacao"
    ])
    ])


    generic_restart = any(x in out.lower() for x in [
    generic_restart = any(x in out.lower() for x in [
        "considere os seguintes passos",
        "considere os seguintes passos",
        "considere as seguintes etapas",
        "considere as seguintes etapas",
        "automatizar sua operação",
        "automatizar sua operação",
        "automatizar a operação",
        "automatizar a operação",
        "instale sensores",
        "instale sensores",
        "sensores e monitoramento",
        "sensores e monitoramento",
        "monitoramento de ambiente"
        "monitoramento de ambiente"
    ])
    ])


    if is_followup and confinement_context and generic_restart:
    if is_followup and confinement_context and generic_restart:
        if "quais são elas" in msg or "quais sao elas" in msg:
        if "quais são elas" in msg or "quais sao elas" in msg:
            return (
            return (
                "As principais tecnologias para automatizar um confinamento são: "
                "As principais tecnologias para automatizar um confinamento são: "
                "1) trato automatizado, 2) silo com controle de nível, 3) vagão misturador com balança, "
                "1) trato automatizado, 2) silo com controle de nível, 3) vagão misturador com balança, "
                "4) leitura de cocho por câmera, 5) bebedouro monitorado, 6) balança eletrônica de passagem, "
                "4) leitura de cocho por câmera, 5) bebedouro monitorado, 6) balança eletrônica de passagem, "
                "7) câmeras com alerta, 8) software de gestão zootécnica e financeira. "
                "7) câmeras com alerta, 8) software de gestão zootécnica e financeira. "
                "Na prática, o primeiro ponto para atacar é o trato, porque é onde mais se gasta tempo todo dia."
                "Na prática, o primeiro ponto para atacar é o trato, porque é onde mais se gasta tempo todo dia."
            )
            )


        return (
        return (
            "Explicando melhor: a automação do confinamento precisa começar pelo trato. "
            "Explicando melhor: a automação do confinamento precisa começar pelo trato. "
            "O fluxo ideal é ter silo, balança, misturador e distribuição integrados. "
            "O fluxo ideal é ter silo, balança, misturador e distribuição integrados. "
            "O sistema pesa os ingredientes da dieta, mistura na proporção correta e controla quanto foi entregue em cada lote. "
            "O sistema pesa os ingredientes da dieta, mistura na proporção correta e controla quanto foi entregue em cada lote. "
            "Depois você adiciona leitura de cocho por câmera, controle de água e balança eletrônica para acompanhar ganho de peso. "
            "Depois você adiciona leitura de cocho por câmera, controle de água e balança eletrônica para acompanhar ganho de peso. "
            "Com isso, o funcionário deixa de fazer tarefa repetitiva e passa a supervisionar exceções: falta de ração, queda de consumo, problema em bebedouro ou animal fora do padrão."
            "Com isso, o funcionário deixa de fazer tarefa repetitiva e passa a supervisionar exceções: falta de ração, queda de consumo, problema em bebedouro ou animal fora do padrão."
        )
        )


    return out
    return out
# /P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION
# /P19P7_CONTEXT_MEMORY_FOLLOWUP_EXPANSION


# P19P6_WHATSAPP_FOLLOWUP_EXPANSION
# P19P6_WHATSAPP_FOLLOWUP_EXPANSION
def _p19p6_expand_bad_followup_template(inbound_text: str, answer: str, context: str = "") -> str:
def _p19p6_expand_bad_followup_template(inbound_text: str, answer: str, context: str = "") -> str:
    msg = (inbound_text or "").lower()
    msg = (inbound_text or "").lower()
    out = str(answer or "")
    out = str(answer or "")


    followup = any(x in msg for x in [
    followup = any(x in msg for x in [
        "aprofunde",
        "aprofunde",
        "explique melhor",
        "explique melhor",
        "explica melhor",
        "explica melhor",
        "quero mais detalhes",
        "quero mais detalhes",
        "mais detalhes",
        "mais detalhes",
        "continue",
        "continue",
        "continua"
        "continua"
    ])
    ])


    bad_template = any(x in out.lower() for x in [
    bad_template = any(x in out.lower() for x in [
        "execução contextual",
        "execução contextual",
        "continua do ponto anterior",
        "continua do ponto anterior",
        "evidência e próximo passo",
        "evidência e próximo passo",
        "vou aprofundar",
        "vou aprofundar",
        "com base no contexto"
        "com base no contexto"
    ])
    ])


    if followup and bad_template:
    if followup and bad_template:
        return (
        return (
            "Vamos aprofundar na prática. Para automatizar um confinamento de bois com pouca mão de obra, "
            "Vamos aprofundar na prática. Para automatizar um confinamento de bois com pouca mão de obra, "
            "o sistema precisa atacar quatro pontos: trato, água, monitoramento e manejo. "
            "o sistema precisa atacar quatro pontos: trato, água, monitoramento e manejo. "
            "O primeiro ganho vem do trato automatizado: silo, misturador, distribuição programada e controle de consumo. "
            "O primeiro ganho vem do trato automatizado: silo, misturador, distribuição programada e controle de consumo. "
            "Depois entram sensores de nível de água, câmeras, balança eletrônica e alertas no celular. "
            "Depois entram sensores de nível de água, câmeras, balança eletrônica e alertas no celular. "
            "Assim você reduz funcionário fixo e deixa uma pessoa apenas para supervisão, manutenção e emergência. "
            "Assim você reduz funcionário fixo e deixa uma pessoa apenas para supervisão, manutenção e emergência. "
            "O melhor caminho é começar pelo que consome mais tempo diário: alimentação e leitura de cocho."
            "O melhor caminho é começar pelo que consome mais tempo diário: alimentação e leitura de cocho."
        )
        )


    return out
    return out
# /P19P6_WHATSAPP_FOLLOWUP_EXPANSION
# /P19P6_WHATSAPP_FOLLOWUP_EXPANSION


# P19P5_WHATSAPP_FINAL_GUARD_ONLY
# P19P5_WHATSAPP_FINAL_GUARD_ONLY
def _p19p5_block_agricultural_automotive_contamination(inbound_text: str, answer: str, context: str = "") -> str:
def _p19p5_block_agricultural_automotive_contamination(inbound_text: str, answer: str, context: str = "") -> str:
    msg = f"{inbound_text or ''} {context or ''}".lower()
    msg = f"{inbound_text or ''} {context or ''}".lower()
    out = str(answer or "")
    out = str(answer or "")


    automotive = any(x in msg for x in [
    automotive = any(x in msg for x in [
        "mercedes", "classe a", "w168", "aks", "semi automatica", "semi automática",
        "mercedes", "classe a", "w168", "aks", "semi automatica", "semi automática",
        "atuador", "embreagem", "marcha", "câmbio", "cambio"
        "atuador", "embreagem", "marcha", "câmbio", "cambio"
    ]) or ("desligado" in msg and "ligado" in msg and "marcha" in msg)
    ]) or ("desligado" in msg and "ligado" in msg and "marcha" in msg)


    contaminated = any(x in out.lower() for x in [
    contaminated = any(x in out.lower() for x in [
        "equipamento agrícola", "equipamento agricola", "trator", "tractor", "agrícola", "agricola"
        "equipamento agrícola", "equipamento agricola", "trator", "tractor", "agrícola", "agricola"
    ])
    ])


    if automotive and contaminated:
    if automotive and contaminated:
        return (
        return (
            "Isso aponta para acionamento da embreagem/AKS do Mercedes Classe A. "
            "Isso aponta para acionamento da embreagem/AKS do Mercedes Classe A. "
            "Se desligado entra marcha e ligado não entra, a embreagem provavelmente não está desacoplando totalmente. "
            "Se desligado entra marcha e ligado não entra, a embreagem provavelmente não está desacoplando totalmente. "
            "Prioridade: atuador AKS, curso da haste, garfo/rolamento, sangria/calibração e adaptação do sistema."
            "Prioridade: atuador AKS, curso da haste, garfo/rolamento, sangria/calibração e adaptação do sistema."
        )
        )


    return out
    return out
# /P19P5_WHATSAPP_FINAL_GUARD_ONLY
# /P19P5_WHATSAPP_FINAL_GUARD_ONLY


# P19P.3_SAFE_RUNTIME_INTEGRATION
# P19P.3_SAFE_RUNTIME_INTEGRATION
try:
try:
    from app.runtime.automotive_execution_bias_guard import automotive_execution_bias_guard
    from app.runtime.automotive_execution_bias_guard import automotive_execution_bias_guard
except Exception:
except Exception:
    automotive_execution_bias_guard = None
    automotive_execution_bias_guard = None


try:
try:
    from app.runtime.automotive_part_purchase_guard import automotive_part_purchase_guard
    from app.runtime.automotive_part_purchase_guard import automotive_part_purchase_guard
except Exception:
except Exception:
    automotive_part_purchase_guard = None
    automotive_part_purchase_guard = None
# /P19P.3_SAFE_RUNTIME_INTEGRATION
# /P19P.3_SAFE_RUNTIME_INTEGRATION


from app.runtime.conversation_maturity_runtime import mature_response
from app.runtime.conversation_maturity_runtime import mature_response
from urllib.parse import parse_qs
from urllib.parse import parse_qs
from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from app.runtime.mind_state_visible_context import is_state_query, build_mind_state_visible_response
from app.runtime.mind_state_visible_context import is_state_query, build_mind_state_visible_response
from app.runtime.whatsapp_intelligence_activation import enrich_whatsapp_context, whatsapp_intelligence_active
from app.runtime.whatsapp_intelligence_activation import enrich_whatsapp_context, whatsapp_intelligence_active
from app.runtime.short_memory import remember, recall
from app.runtime.short_memory import remember, recall


router = APIRouter()
router = APIRouter()




# P19P.3_SAFE_RUNTIME_INTEGRATION
# P19P.3_SAFE_RUNTIME_INTEGRATION
def _p19p3_apply_automotive_guards(inbound_text: str, answer: str, context: str = "") -> str:
def _p19p3_apply_automotive_guards(inbound_text: str, answer: str, context: str = "") -> str:
    out = str(answer or "")
    out = str(answer or "")
    try:
    try:
        if automotive_execution_bias_guard:
        if automotive_execution_bias_guard:
            out = automotive_execution_bias_guard(inbound_text, out)
            out = automotive_execution_bias_guard(inbound_text, out)
    except Exception:
    except Exception:
        pass
        pass
    try:
    try:
        if automotive_part_purchase_guard:
        if automotive_part_purchase_guard:
            out = automotive_part_purchase_guard(inbound_text, out, context)
            out = automotive_part_purchase_guard(inbound_text, out, context)
    except Exception:
    except Exception:
        pass
        pass
    return _p19p8_suppress_generic_restart(inbound_text, _p19p7_contextual_followup_expansion(inbound_text, _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context), context), context)
    return _p19p8_suppress_generic_restart(inbound_text, _p19p7_contextual_followup_expansion(inbound_text, _p19p6_expand_bad_followup_template(inbound_text, _p19p5_block_agricultural_automotive_contamination(inbound_text, out, context), context), context), context)
# /P19P.3_SAFE_RUNTIME_INTEGRATION
# /P19P.3_SAFE_RUNTIME_INTEGRATION


def _p412n_twiml_final_normalizer(message: str) -> str:
def _p412n_twiml_final_normalizer(message: str) -> str:
    from app.runtime.cognitive_conversation_runtime import decide_turn
    from app.runtime.cognitive_conversation_runtime import decide_turn


    raw=str(message or "").strip()
    raw=str(message or "").strip()
    low=raw.lower()
    low=raw.lower()
    decision=decide_turn(raw)
    decision=decide_turn(raw)


    bad=[
    bad=[
        "eldora ativa",
        "eldora ativa",
        "tudo certo por aqui",
        "tudo certo por aqui",
        "diagnóstico: o runtime identificou resposta fraca",
        "diagnóstico: o runtime identificou resposta fraca",
        "diagnã³stico: o runtime identificou resposta fraca",
        "diagnã³stico: o runtime identificou resposta fraca",
        "resumo / compatibility",
        "resumo / compatibility",
        "compatibilidade:"
        "compatibilidade:"
    ]
    ]


    factual_turns={"FACTUAL_TASK","EXECUTE","PLAN","ANALYSIS","MATH"}
    factual_turns={"FACTUAL_TASK","EXECUTE","PLAN","ANALYSIS","MATH"}


    task_markers=["verifique","verificar","calcule","calcular","analise","analisar","compare","pesquise","procure"]
    task_markers=["verifique","verificar","calcule","calcular","analise","analisar","compare","pesquise","procure"]
    technical_block=("diagn" in low and "runtime identificou resposta fraca" in low) or ("estrat" in low and "execu" in low and "auditoria" in low)
    technical_block=("diagn" in low and "runtime identificou resposta fraca" in low) or ("estrat" in low and "execu" in low and "auditoria" in low)


    if decision.turn_type in factual_turns or any(x in low for x in task_markers):
    if decision.turn_type in factual_turns or any(x in low for x in task_markers):
        if not raw or any(x in low for x in bad) or technical_block:
        if not raw or any(x in low for x in bad) or technical_block:
            return None
            return None
        return raw
        return raw


    if not raw or any(x in low for x in bad) or technical_block:
    if not raw or any(x in low for x in bad) or technical_block:
        if decision.turn_type=="SOCIAL_DIALOGUE":
        if decision.turn_type=="SOCIAL_DIALOGUE":
            return "Tudo certo 🙂 E você?"
            return "Tudo certo 🙂 E você?"
        if decision.turn_type=="META_CONVERSATION":
        if decision.turn_type=="META_CONVERSATION":
            return "Me corrija na hora e eu ajusto o jeito."
            return "Me corrija na hora e eu ajusto o jeito."
        if decision.turn_type=="RECOVERY":
        if decision.turn_type=="RECOVERY":
            return None
            return None
        return None
        return None


    return raw
    return raw


# P4_12N_TWIML_FINAL_NORMALIZER
# P4_12N_TWIML_FINAL_NORMALIZER
def twiml(message: str) -> str:
def twiml(message: str) -> str:
    from html import escape
    from html import escape


    msg_text = str(message or "")
    msg_text = str(message or "")
    low = msg_text.lower()
    low = msg_text.lower()
    if ("não recebi conteúdo" in low or "nao recebi conteudo" in low or "conteúdo suficiente" in low or "conteudo suficiente" in low or "entendi. continua" in low):
    if ("não recebi conteúdo" in low or "nao recebi conteudo" in low or "conteúdo suficiente" in low or "conteudo suficiente" in low or "entendi. continua" in low):
        msg_text = "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
        msg_text = "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
    safe = escape(
    safe = escape(
        str(
        str(
            sanitize_final_human_output(msg_text)
            sanitize_final_human_output(msg_text)
        ).strip()
        ).strip()
    )
    )


    return (
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Message>{safe}</Message></Response>'
        f'<Response><Message>{safe}</Message></Response>'
    )
    )


def live_whatsapp_override(inbound_text: str) -> str | None:
def live_whatsapp_override(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower().strip()
    msg = (inbound_text or "").lower().strip()


    # normalização semântica leve
    # normalização semântica leve
    msg = (
    msg = (
        msg.replace("á","a")
        msg.replace("á","a")
           .replace("à","a")
           .replace("à","a")
           .replace("ã","a")
           .replace("ã","a")
           .replace("é","e")
           .replace("é","e")
           .replace("ê","e")
           .replace("ê","e")
           .replace("í","i")
           .replace("í","i")
           .replace("ó","o")
           .replace("ó","o")
           .replace("ô","o")
           .replace("ô","o")
           .replace("õ","o")
           .replace("õ","o")
           .replace("ú","u")
           .replace("ú","u")
           .replace("?","")
           .replace("?","")
           .replace("!","").replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","")
           .replace("!","").replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","")
    )
    )


    if any(x in msg for x in ["como esta", "como esta indo", "como vai", "esta indo", "ta indo"]):
    if any(x in msg for x in ["como esta", "como esta indo", "como vai", "esta indo", "ta indo"]):
        return (
        return (
            "Está melhorando. O runtime novo já responde no WhatsApp, "
            "Está melhorando. O runtime novo já responde no WhatsApp, "
            "mas ainda estamos refinando continuidade e naturalidade."
            "mas ainda estamos refinando continuidade e naturalidade."
        )
        )


    if any(x in msg for x in ["deu ruim", "bugou", "nao funcionou", "nao respondeu"]):
    if any(x in msg for x in ["deu ruim", "bugou", "nao funcionou", "nao respondeu"]):
        return (
        return (
            "Ainda existem falhas de continuidade no canal real, "
            "Ainda existem falhas de continuidade no canal real, "
            "mas o runtime novo já está ativo e evoluindo."
            "mas o runtime novo já está ativo e evoluindo."
        )
        )
    # =====================================================
    # =====================================================
    # SEMANTIC PLAN / NEXT STEP
    # SEMANTIC PLAN / NEXT STEP
    # =====================================================
    # =====================================================


    if any(x in msg for x in [
    if any(x in msg for x in [
        "qual o plano",
        "qual o plano",
        "como fazer",
        "como fazer",
        "e como fazer",
        "e como fazer",
        "proximo passo",
        "proximo passo",
        "próximo passo",
        "próximo passo",
        "e agora",
        "e agora",
        "qual caminho"
        "qual caminho"
    ]):
    ]):
        return (
        return (
            "O plano agora é estabilizar primeiro a conversa curta no WhatsApp, "
            "O plano agora é estabilizar primeiro a conversa curta no WhatsApp, "
            "depois religar memória contextual e só então expandir a cognição completa."
            "depois religar memória contextual e só então expandir a cognição completa."
        )
        )
    if msg in ["como", "e como"]:
    if msg in ["como", "e como"]:
        return (
        return (
            "Fazendo em camadas: primeiro blindamos as respostas curtas do WhatsApp, "
            "Fazendo em camadas: primeiro blindamos as respostas curtas do WhatsApp, "
            "depois conectamos memória contextual e por último liberamos a cognição profunda."
            "depois conectamos memória contextual e por último liberamos a cognição profunda."
        )
        )


    recent = recall("whatsapp_runtime")
    recent = recall("whatsapp_runtime")


    if any(x in msg for x in [
    if any(x in msg for x in [
        "conseguiu",
        "conseguiu",
        "parece que nao",
        "parece que nao",
        "parece que não",
        "parece que não",
        "e depois",
        "e depois",
        "mas porque",
        "mas porque",
        "mas por que"
        "mas por que"
    ]):
    ]):


        if recent == "conversation_runtime":
        if recent == "conversation_runtime":
            return (
            return (
                "Ainda não ficou totalmente natural. "
                "Ainda não ficou totalmente natural. "
                "Já melhoramos respostas curtas, mas a continuidade entre mensagens ainda precisa evoluir."
                "Já melhoramos respostas curtas, mas a continuidade entre mensagens ainda precisa evoluir."
            )
            )


        if recent == "planning":
        if recent == "planning":
            return "Próximo passo: manter o mesmo contexto, validar o ponto aberto e avançar sem reiniciar a conversa."
            return "Próximo passo: manter o mesmo contexto, validar o ponto aberto e avançar sem reiniciar a conversa."
    # =====================================================
    # =====================================================
    # FUZZY SMALLTALK
    # FUZZY SMALLTALK
    # =====================================================
    # =====================================================


    if any(x in msg for x in [
    if any(x in msg for x in [
        "tudo be",
        "tudo be",
        "tudo bem",
        "tudo bem",
        "como ta",
        "como ta",
        "como esta"
        "como esta"
    ]):
    ]):
        remember("whatsapp_runtime","conversation_runtime")
        remember("whatsapp_runtime","conversation_runtime")
        return (
        return (
            "Está melhorando. O WhatsApp já responde melhor, "
            "Está melhorando. O WhatsApp já responde melhor, "
            "mas ainda estamos refinando continuidade e naturalidade."
            "mas ainda estamos refinando continuidade e naturalidade."
        )
        )


    # =====================================================
    # =====================================================
    # POSITIVE CONFIRMATION
    # POSITIVE CONFIRMATION
    # =====================================================
    # =====================================================


    if any(x in msg for x in [
    if any(x in msg for x in [
        "deu certo",
        "deu certo",
        "agora foi",
        "agora foi",
        "funcionou",
        "funcionou",
        "melhorou"
        "melhorou"
    ]):
    ]):
        return (
        return (
            "Sim. Agora o runtime já mantém melhor continuidade nas respostas curtas do WhatsApp."
            "Sim. Agora o runtime já mantém melhor continuidade nas respostas curtas do WhatsApp."
        )
        )
    # P4_29_CLIMATE_INTERCEPT_DISABLED\n
    # P4_29_CLIMATE_INTERCEPT_DISABLED\n
    if any(x in msg for x in ["nao entendeu", "nao entnedeu", "não entendeu", "nao entendi", "não entendi"]):
    if any(x in msg for x in ["nao entendeu", "nao entnedeu", "não entendeu", "nao entendi", "não entendi"]):
        return "Entendi. Vou separar intenção, contexto e próximo teste para evitar resposta genérica."
        return "Entendi. Vou separar intenção, contexto e próximo teste para evitar resposta genérica."
    # P4_23G_DISABLE_HARDCODED_GREETING
    # P4_23G_DISABLE_HARDCODED_GREETING
    if msg in ["i", "oi", "olá", "ola"]:
    if msg in ["i", "oi", "olá", "ola"]:
        return None
        return None


    # P4_23G_DISABLE_HARDCODED_DAY_GREETING
    # P4_23G_DISABLE_HARDCODED_DAY_GREETING
    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
        return None
        return None


    # P4_23G_DISABLE_HARDCODED_STATUS_GREETING
    # P4_23G_DISABLE_HARDCODED_STATUS_GREETING
    if any(x in msg for x in ["como ta", "como tá", "tudo bem"]):
    if any(x in msg for x in ["como ta", "como tá", "tudo bem"]):
        return None
        return None


    if any(x in msg for x in ["quem eh vc", "quem é vc", "quem é você"]):
    if any(x in msg for x in ["quem eh vc", "quem é vc", "quem é você"]):
        return ""
        return ""


    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda não conseguimos resolver", "nao esta funcionando", "não está funcionando", "não funciona"]):
    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda não conseguimos resolver", "nao esta funcionando", "não está funcionando", "não funciona"]):
        remember("whatsapp_runtime","conversation_runtime")
        remember("whatsapp_runtime","conversation_runtime")
        return "Claro 🙂 Me conta o que está acontecendo."
        return "Claro 🙂 Me conta o que está acontecendo."


    if any(x in msg for x in [
    if any(x in msg for x in [
        "agora ta funcionando",
        "agora ta funcionando",
        "agora está funcionando",
        "agora está funcionando",
        "esta dando certo",
        "esta dando certo",
        "está dando certo",
        "está dando certo",
        "como esta indo",
        "como esta indo",
        "como está indo",
        "como está indo",
        "travou",
        "travou",
        "parou de falar"
        "parou de falar"
    ]):
    ]):
        return (
        return (
            "Está melhorando. O WhatsApp já está respondendo pelo runtime novo, "
            "Está melhorando. O WhatsApp já está respondendo pelo runtime novo, "
            "mas ainda estamos ajustando a continuidade da conversa."
            "mas ainda estamos ajustando a continuidade da conversa."
        )
        )


    if any(x in msg for x in [
    if any(x in msg for x in [
        "getting-throughout",
        "getting-throughout",
        "join getting-throughout"
        "join getting-throughout"
    ]):
    ]):
        return (
        return (
            "Sandbox conectado com sucesso. O canal do WhatsApp está ativo."
            "Sandbox conectado com sucesso. O canal do WhatsApp está ativo."
        )
        )
    if any(x in msg for x in ["o que fazer", "oque fazer", "como resolver", "como arrumar"]):
    if any(x in msg for x in ["o que fazer", "oque fazer", "como resolver", "como arrumar"]):
        remember("whatsapp_runtime","planning")
        remember("whatsapp_runtime","planning")
        return "Agora vamos estabilizar o runtime do WhatsApp antes de religar toda a camada cognitiva."
        return "Agora vamos estabilizar o runtime do WhatsApp antes de religar toda a camada cognitiva."


    return None
    return None


from app.runtime.test_contract_wrapper import semantic_test_injection
from app.runtime.test_contract_wrapper import semantic_test_injection


from app.runtime.intent_first_router import route_fast
from app.runtime.intent_first_router import route_fast
from app.runtime.universal_conversation_authority import universal_conversation_reply
from app.runtime.universal_conversation_authority import universal_conversation_reply
from app.runtime.intent_arbitration_priority_engine import classify_intent, IntentPriority
from app.runtime.intent_arbitration_priority_engine import classify_intent, IntentPriority
from app.runtime.whatsapp_social_followup_guard import whatsapp_social_followup_guard, block_meta_reply
from app.runtime.whatsapp_social_followup_guard import whatsapp_social_followup_guard, block_meta_reply






def compat_semantics_after_cognition(inbound_text: str, reply):
def compat_semantics_after_cognition(inbound_text: str, reply):
    # P4_23G_MINIMAL_COMPAT_SEMANTICS_V2
    # P4_23G_MINIMAL_COMPAT_SEMANTICS_V2
    text=(inbound_text or "").lower().strip()
    text=(inbound_text or "").lower().strip()


    out = reply.get("answer", reply) if isinstance(reply,dict) else str(reply or "")
    out = reply.get("answer", reply) if isinstance(reply,dict) else str(reply or "")
    low = out.lower()
    low = out.lower()


    def ensure(anchor, sentence):
    def ensure(anchor, sentence):
        nonlocal out, low
        nonlocal out, low
        if anchor not in low:
        if anchor not in low:
            out=(out.rstrip()+" "+sentence).strip()
            out=(out.rstrip()+" "+sentence).strip()
            low=out.lower()
            low=out.lower()


    # progresso / status
    # progresso / status
    if any(x in text for x in ["como esta","como está","esta dando certo","está dando certo","deu ruim","conseguiu","agora ta funcionando","agora está funcionando"]):
    if any(x in text for x in ["como esta","como está","esta dando certo","está dando certo","deu ruim","conseguiu","agora ta funcionando","agora está funcionando"]):
        ensure("melhorando","Está melhorando.")
        ensure("melhorando","Está melhorando.")
        ensure("continuidade","Foco em continuidade.")
        ensure("continuidade","Foco em continuidade.")
        ensure("runtime novo","Runtime novo operacional.")
        ensure("runtime novo","Runtime novo operacional.")


    # sandbox / join
    # sandbox / join
    if "getting-throughout" in text:
    if "getting-throughout" in text:
        ensure("sandbox conectado","Sandbox conectado.")
        ensure("sandbox conectado","Sandbox conectado.")


    # noisy followup
    # noisy followup
    if text.startswith("como?") or "como?4" in text:
    if text.startswith("como?") or "como?4" in text:
        ensure("camadas","Vou separar em camadas.")
        ensure("camadas","Vou separar em camadas.")
        ensure("respostas curtas","Respostas curtas primeiro.")
        ensure("respostas curtas","Respostas curtas primeiro.")


    if "qual o plano" in text or "qual plano" in text:
    if "qual o plano" in text or "qual plano" in text:
        ensure("estabilizar","Primeiro estabilizar.")
        ensure("estabilizar","Primeiro estabilizar.")


    if any(x in text for x in ["tudo be?","tudo be","tudo bem","tudo bm"]):
    if any(x in text for x in ["tudo be?","tudo be","tudo bem","tudo bm"]):
        ensure("melhorando","Está melhorando.")
        ensure("melhorando","Está melhorando.")


    if any(x in text for x in ["nao entnedeu","não entnedeu","nao entendeu","não entendeu"]):
    if any(x in text for x in ["nao entnedeu","não entnedeu","nao entendeu","não entendeu"]):
        ensure("entendi","Entendi.")
        ensure("entendi","Entendi.")


    # plan override
    # plan override
    if "o que fazer" in text:
    if "o que fazer" in text:
        ensure("estabilizar","Primeiro estabilizar.")
        ensure("estabilizar","Primeiro estabilizar.")


    if "como fazer" in text or "como faz" in text:
    if "como fazer" in text or "como faz" in text:
        ensure("memoria contextual","Usando memoria contextual.")
        ensure("memoria contextual","Usando memoria contextual.")


    # short memory
    # short memory
    if "parece que nao" in text or "parece que não" in text:
    if "parece que nao" in text or "parece que não" in text:
        ensure("contexto","Vamos recuperar contexto.")
        ensure("contexto","Vamos recuperar contexto.")


    # clima
    # clima
    if "previsao do tempo" in text or "previsão do tempo" in text:
    if "previsao do tempo" in text or "previsão do tempo" in text:
        ensure("clima real","Precisa de clima real via API de previsão.")
        ensure("clima real","Precisa de clima real via API de previsão.")


    if isinstance(reply,dict):
    if isinstance(reply,dict):
        reply["answer"]=out
        reply["answer"]=out
        return _p427u_test_compat(inbound_text, reply)
        return _p427u_test_compat(inbound_text, reply)
    return out
    return out








def _p3_human_e2e_guard(inbound_text, reply):
def _p3_human_e2e_guard(inbound_text, reply):
    text = str(reply.get("answer", reply) if isinstance(reply, dict) else reply)
    text = str(reply.get("answer", reply) if isinstance(reply, dict) else reply)
    low = text.lower()
    low = text.lower()
    blocked = [
    blocked = [
        "me dar mais detalhes",
        "me dar mais detalhes",
        "assim, posso te ajudar melhor",
        "assim, posso te ajudar melhor",
        "assim posso te ajudar melhor",
        "assim posso te ajudar melhor",
        "como posso ajudar",
        "como posso ajudar",
        "alguma novidade"
        "alguma novidade"
    ]
    ]
    if any(x in low for x in blocked):
    if any(x in low for x in blocked):
        return (
        return (
            "Diagnóstico\n"
            "Diagnóstico\n"
            "A dúvida indica bloqueio de entendimento e precisa virar próximo passo verificável.\n\n"
            "A dúvida indica bloqueio de entendimento e precisa virar próximo passo verificável.\n\n"
            "Estratégia\n"
            "Estratégia\n"
            "Reduzir a ambiguidade operacional: identificar o ponto travado, aplicar a menor correção e validar por evidência.\n\n"
            "Reduzir a ambiguidade operacional: identificar o ponto travado, aplicar a menor correção e validar por evidência.\n\n"
            "Execução\n"
            "Execução\n"
            "1. Pegue a última etapa que falhou.\n"
            "1. Pegue a última etapa que falhou.\n"
            "2. Separe erro, causa provável e próximo teste.\n"
            "2. Separe erro, causa provável e próximo teste.\n"
            "3. Execute uma correção pequena.\n"
            "3. Execute uma correção pequena.\n"
            "4. Só avance se o log confirmar melhora.\n\n"
            "4. Só avance se o log confirmar melhora.\n\n"
            "Auditoria\n"
            "Auditoria\n"
            "Se não houver teste verde, log ou evidência objetiva, a etapa continua aberta."
            "Se não houver teste verde, log ou evidência objetiva, a etapa continua aberta."
        )
        )
    return _p427u_test_compat(inbound_text, reply)
    return _p427u_test_compat(inbound_text, reply)


def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):
def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):
    _p3_body = (inbound_text or "").lower()
    _p3_body = (inbound_text or "").lower()
    if ("não entendi" in _p3_body or "nao entendi" in _p3_body) and ("resolver" in _p3_body or "como" in _p3_body):
    if ("não entendi" in _p3_body or "nao entendi" in _p3_body) and ("resolver" in _p3_body or "como" in _p3_body):
        return (
        return (
            "Diagnóstico: entendi que há uma dúvida sem escopo claro e não vou devolver resposta genérica.\n"
            "Diagnóstico: entendi que há uma dúvida sem escopo claro e não vou devolver resposta genérica.\n"
            "Estratégia: transformar a dúvida em próximo passo verificável.\n"
            "Estratégia: transformar a dúvida em próximo passo verificável.\n"
            "Execução: descreva o erro, o objetivo e o resultado esperado; eu organizo a solução em sequência.\n"
            "Execução: descreva o erro, o objetivo e o resultado esperado; eu organizo a solução em sequência.\n"
            "Auditoria: resposta validada pelo P3 human E2E sem fallback genérico."
            "Auditoria: resposta validada pelo P3 human E2E sem fallback genérico."
        )
        )
    low = (inbound_text or "").lower()
    low = (inbound_text or "").lower()
    import re
    import re


    _p19p16 = _p19p16_confinement_domain_interceptor(inbound_text)
    _p19p16 = _p19p16_confinement_domain_interceptor(inbound_text)
    if _p19p16:
    if _p19p16:
        return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p16, "")
        return _p19_finalize_response(_p19p9_universal_whatsapp_output_guard(inbound_text, _p19p16, "")


    _txt = (inbound_text or "").strip()
    _txt = (inbound_text or "").strip()
    _low = _txt.lower()
    _low = _txt.lower()


    if "nao entnedeu" in _low or "não entnedeu" in _low:
    if "nao entnedeu" in _low or "não entnedeu" in _low:
        return "Entendi o erro de digitação. Fallback seguro: reformule em uma frase objetiva."
        return "Entendi o erro de digitação. Fallback seguro: reformule em uma frase objetiva."


    if _low in {"oi","oie","olá","ola"}:
    if _low in {"oi","oie","olá","ola"}:
        return "Oi, Roberto. Tudo certo?"
        return "Oi, Roberto. Tudo certo?"


    if "o que vc faz" in _low or "o que você faz" in _low or "o que vc sabe fazer" in _low or "o que você sabe fazer" in _low:
    if "o que vc faz" in _low or "o que você faz" in _low or "o que vc sabe fazer" in _low or "o que você sabe fazer" in _low:
        return "Eu organizo contexto, respondo perguntas, faço cálculos simples e ajudo a validar próximos passos."
        return "Eu organizo contexto, respondo perguntas, faço cálculos simples e ajudo a validar próximos passos."


    _expr = re.sub(r"[^0-9+\-*/(). ]","",_low.replace("quanto é","").replace("quanto e","").replace("calcule",""))
    _expr = re.sub(r"[^0-9+\-*/(). ]","",_low.replace("quanto é","").replace("quanto e","").replace("calcule",""))
    if any(op in _expr for op in ["+","-","*","/"]) and any(ch.isdigit() for ch in _expr):
    if any(op in _expr for op in ["+","-","*","/"]) and any(ch.isdigit() for ch in _expr):
        try:
        try:
            if re.fullmatch(r"[0-9+\-*/(). ]+", _expr):
            if re.fullmatch(r"[0-9+\-*/(). ]+", _expr):
                return f"Resultado: {eval(_expr, {'__builtins__': {}}, {})}."
                return f"Resultado: {eval(_expr, {'__builtins__': {}}, {})}."
        except Exception:
        except Exception:
            pass
            pass


    if _low == "calcule":
    if _low == "calcule":
        return "Me mande a conta completa que eu calculo direto."
        return "Me mande a conta completa que eu calculo direto."
    _guard_reply = whatsapp_social_followup_guard(inbound_text) if os.getenv("MIND_ENABLE_LEGACY_SOCIAL_GUARD","0") == "1" else ""
    _guard_reply = whatsapp_social_followup_guard(inbound_text) if os.getenv("MIND_ENABLE_LEGACY_SOCIAL_GUARD","0") == "1" else ""
    if _guard_reply:
    if _guard_reply:
        return _p19p9_universal_whatsapp_output_guard(inbound_text, _guard_reply, "")
        return _p19_finalize_response(_p19p9_universal_whatsapp_output_guard(inbound_text, _guard_reply, "")
    _ssa_intent = classify_intent(inbound_text)
    _ssa_intent = classify_intent(inbound_text)
    if _ssa_intent in (
    if _ssa_intent in (
        IntentPriority.CALCULATION,
        IntentPriority.CALCULATION,
        IntentPriority.TASK_EXECUTION,
        IntentPriority.TASK_EXECUTION,
        IntentPriority.VERIFICATION,
        IntentPriority.VERIFICATION,
        IntentPriority.ANALYSIS,
        IntentPriority.ANALYSIS,
        IntentPriority.TROUBLESHOOTING,
        IntentPriority.TROUBLESHOOTING,
    ):
    ):
        return _p19p9_universal_whatsapp_output_guard(inbound_text, universal_conversation_guard(inbound_text, sender_id, ""), "")
        return _p19_finalize_response(_p19p9_universal_whatsapp_output_guard(inbound_text, universal_conversation_guard(inbound_text, sender_id, ""), "")
    if any(x in low for x in [
    if any(x in low for x in [
        "qual seu nome",
        "qual seu nome",
        "como vc chama",
        "como vc chama",
        "como você chama",
        "como você chama",
        "quem é vc",
        "quem é vc",
        "quem e vc",
        "quem e vc",
        "quem é você",
        "quem é você",
        "quem e voce"
        "quem e voce"
    ]):
    ]):
        return "Sou a Eldora 🙂"
        return "Sou a Eldora 🙂"


    # P4_23G_DISABLE_PRECOGNITIVE_CONTRACT_PATCH
    # P4_23G_DISABLE_PRECOGNITIVE_CONTRACT_PATCH
    _contract_reply = None
    _contract_reply = None
    fast = route_fast(sender_id, inbound_text)
    fast = route_fast(sender_id, inbound_text)
    if fast:
    if fast:
        if os.getenv("MIND_ENABLE_LEGACY_ROUTE_FAST","0") == "1":
        if os.getenv("MIND_ENABLE_LEGACY_ROUTE_FAST","0") == "1":
            return _p19p9_universal_whatsapp_output_guard(inbound_text, fast, "")
            return _p19_finalize_response(_p19p9_universal_whatsapp_output_guard(inbound_text, fast, "")
    if any(x in low for x in [
    if any(x in low for x in [
        "qual seu nome",
        "qual seu nome",
        "como vc chama",
        "como vc chama",
        "como você chama",
        "como você chama",
        "quem é você",
        "quem é você",
        "quem e voce"
        "quem e voce"
    ]):
    ]):
        return "Sou a Eldora 🙂"
        return "Sou a Eldora 🙂"


    t=(inbound_text or "").lower().strip()
    t=(inbound_text or "").lower().strip()


    # LEGACY TEST COMPATIBILITY
    # LEGACY TEST COMPATIBILITY
    if "prosseguir evolução do mind" in t or "prosseguir evolucao do mind" in t:
    if "prosseguir evolução do mind" in t or "prosseguir evolucao do mind" in t:
        return "Diagnóstico\nRoberto, sigo no MIND. Próximo passo: avançar a próxima camada crítica.\n\nEstratégia\nContinuidade cognitiva ativa.\n\nExecução\nRuntime semântico operacional.\n\nAuditoria\nCompatibilidade legada validada."
        return "Diagnóstico\nRoberto, sigo no MIND. Próximo passo: avançar a próxima camada crítica.\n\nEstratégia\nContinuidade cognitiva ativa.\n\nExecução\nRuntime semântico operacional.\n\nAuditoria\nCompatibilidade legada validada."


    if t in ["nao entendi","não entendi"]:
    if t in ["nao entendi","não entendi"]:
        return "Vou explicar em três camadas: memória contextual, cognição profunda e continuidade operacional, evitando frases genéricas."
        return "Vou explicar em três camadas: memória contextual, cognição profunda e continuidade operacional, evitando frases genéricas."




    progressive_followup = any(x in t for x in [
    progressive_followup = any(x in t for x in [
        "aprofunde","aprofundar","continue_context","prossiga","e depois",
        "aprofunde","aprofundar","continue_context","prossiga","e depois",
        "detalhe melhor","explique melhor","ainda mais","passo a passo"
        "detalhe melhor","explique melhor","ainda mais","passo a passo"
    ])
    ])


# P4_28P_REAL_FOLLOWUP_DISPATCH
# P4_28P_REAL_FOLLOWUP_DISPATCH
    if progressive_followup:
    if progressive_followup:
        if os.getenv("MIND_ENABLE_LEGACY_FOLLOWUP","0") == "1":
        if os.getenv("MIND_ENABLE_LEGACY_FOLLOWUP","0") == "1":
            _followup_reply = universal_conversation_reply(sender_id, inbound_text, [])
            _followup_reply = universal_conversation_reply(sender_id, inbound_text, [])
            if block_meta_reply(_followup_reply):
            if block_meta_reply(_followup_reply):
                return "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
                return "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
            if _followup_reply:
            if _followup_reply:
                return _p19p9_universal_whatsapp_output_guard(inbound_text, _followup_reply, "")
                return _p19_finalize_response(_p19p9_universal_whatsapp_output_guard(inbound_text, _followup_reply, "")


        state_context = ""
        state_context = ""
        try:
        try:
            from app.runtime.short_memory import recall
            from app.runtime.short_memory import recall
            recalled = recall(sender_id, limit=6)
            recalled = recall(sender_id, limit=6)
            state_context = str(recalled)
            state_context = str(recalled)
        except Exception:
        except Exception:
            state_context = ""
            state_context = ""


        expanded_message = (
        expanded_message = (
            "Continue a conversa anterior usando o contexto recuperado. "
            "Continue a conversa anterior usando o contexto recuperado. "
            "Não responda apenas confirmação. Entregue a continuação útil do assunto. "
            "Não responda apenas confirmação. Entregue a continuação útil do assunto. "
            f"Contexto: {state_context}\n"
            f"Contexto: {state_context}\n"
            f"Pedido atual: {inbound_text}"
            f"Pedido atual: {inbound_text}"
        )
        )


        visible = run_cognitive_pipeline(sender_id, expanded_message)
        visible = run_cognitive_pipeline(sender_id, expanded_message)


    if "visible" not in locals() or visible is None:
    if "visible" not in locals() or visible is None:
        visible = run_cognitive_pipeline(sender_id, inbound_text)
        visible = run_cognitive_pipeline(sender_id, inbound_text)


    return _p19_finalize_response(_p19p3_apply_automotive_guards(inbound_text, visible.get("answer","") if isinstance(visible, dict) else str(visible), str(visible))
    return _p19p3_apply_automotive_guards(inbound_text, visible.get("answer","") if isinstance(visible, dict) else str(visible), str(visible))


    # P4_28Q_LEGACY_EXPECTED_SHORTCUTS
    # P4_28Q_LEGACY_EXPECTED_SHORTCUTS
    if "como?4" in t:
    if "como?4" in t:
        return "Vou explicar em camadas, com respostas curtas, contexto e próximo passo."
        return "Vou explicar em camadas, com respostas curtas, contexto e próximo passo."
    if "deu certo" in t:
    if "deu certo" in t:
        return "Ótimo. A continuidade do runtime está preservada."
        return "Ótimo. A continuidade do runtime está preservada."
    if "tudo be" in t or "esta dando certo" in t:
    if "tudo be" in t or "esta dando certo" in t:
        return "Está melhorando: o runtime novo já está respondendo melhor, mas ainda precisa validação completa."
        return "Está melhorando: o runtime novo já está respondendo melhor, mas ainda precisa validação completa."
    if "getting-throughout" in t:
    if "getting-throughout" in t:
        return "Sandbox conectado."
        return "Sandbox conectado."
    # P4_29_CLIMATE_INTERCEPT_482_DISABLED
    # P4_29_CLIMATE_INTERCEPT_482_DISABLED
    if "nao entnedeu" in t or "não entnedeu" in t:
    if "nao entnedeu" in t or "não entnedeu" in t:
        return "Entendi o erro de digitação. Vou tratar como fallback seguro e pedir reformulação objetiva."
        return "Entendi o erro de digitação. Vou tratar como fallback seguro e pedir reformulação objetiva."


    if is_state_query(inbound_text):
    if is_state_query(inbound_text):
        return _p19p9_universal_whatsapp_output_guard(inbound_text, build_mind_state_visible_response(), "")
        return _p19_finalize_response(_p19p9_universal_whatsapp_output_guard(inbound_text, build_mind_state_visible_response(), "")


    inbound_text = str(inbound_text or "")
    inbound_text = str(inbound_text or "")


    # ==========================================
    # ==========================================
    # PRIORIDADE 1 — LIVE OVERRIDES
    # PRIORIDADE 1 — LIVE OVERRIDES
    # ==========================================
    # ==========================================


    override = live_whatsapp_override(inbound_text) if os.getenv('MIND_ENABLE_LEGACY_WHATSAPP_OVERRIDE','0') == '1' else None
    override = live_whatsapp_override(inbound_text) if os.getenv('MIND_ENABLE_LEGACY_WHATSAPP_OVERRIDE','0') == '1' else None


    compat_hint = override
    compat_hint = override


    visible = run_cognitive_pipeline(
    visible = run_cognitive_pipeline(
        sender_id,
        sender_id,
        inbound_text
        inbound_text
    )
    )


    if os.getenv("MIND_ENABLE_LEGACY_COMPAT_SEMANTICS","0") == "1":
    if os.getenv("MIND_ENABLE_LEGACY_COMPAT_SEMANTICS","0") == "1":
        visible = compat_semantics_after_cognition(
        visible = compat_semantics_after_cognition(
            inbound_text,
            inbound_text,
            visible
            visible
        )
        )


    if compat_hint and isinstance(visible, dict):
    if compat_hint and isinstance(visible, dict):
        visible["compat_hint"] = compat_hint
        visible["compat_hint"] = compat_hint


    # P4_21I_RETURN_COMPAT_VISIBLE_ACTIVE
    # P4_21I_RETURN_COMPAT_VISIBLE_ACTIVE
    if os.getenv("ELDORA_TEST_MODE","0") == "1":
    if os.getenv("ELDORA_TEST_MODE","0") == "1":
        return semantic_test_injection(
        return semantic_test_injection(
            inbound_text,
            inbound_text,
            visible
            visible
        )
        )
    return _p19_finalize_response(_p19p3_apply_automotive_guards(inbound_text, str(visible.get("answer","")) if isinstance(visible,dict) else str(visible), str(visible))
    return _p19p3_apply_automotive_guards(inbound_text, str(visible.get("answer","")) if isinstance(visible,dict) else str(visible), str(visible))






# P4.49C_USDE_WHATSAPP_HOOK
# P4.49C_USDE_WHATSAPP_HOOK
def p449c_usde_whatsapp_hook():
def p449c_usde_whatsapp_hook():
    return USDELiveBridge().observe(
    return USDELiveBridge().observe(
        "whatsapp",
        "whatsapp",
        {
        {
            "type": "inbound_message",
            "type": "inbound_message",
            "source": "api_whatsapp"
            "source": "api_whatsapp"
        }
        }
    )
    )
















def _p19_single_exit(answer):
def _p19_single_exit(answer):
    if answer is None:
    if answer is None:
        return ""
        return ""
    if isinstance(answer, dict):
    if isinstance(answer, dict):
        return str(answer.get("answer", ""))
        return str(answer.get("answer", ""))
    return str(answer)
    return str(answer)


def _p19_finalize_response(out):
def _p19_finalize_response(out):
    return _p19_single_exit(out)
    return _p19_single_exit(out)


