from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Optional
import re

class IntentPriority(str, Enum):
    CALCULATION="calculation"
    TASK_EXECUTION="task_execution"
    VERIFICATION="verification"
    ANALYSIS="analysis"
    TROUBLESHOOTING="troubleshooting"
    SOCIAL="social"
    FOLLOWUP_CONTEXTUAL="followup_contextual"
    OPEN_LOOP_CONTINUATION="open_loop_continuation"
    FALLBACK="fallback"

PRIORITY_ORDER=[IntentPriority.CALCULATION,IntentPriority.TASK_EXECUTION,IntentPriority.VERIFICATION,IntentPriority.ANALYSIS,IntentPriority.TROUBLESHOOTING,IntentPriority.SOCIAL,IntentPriority.FOLLOWUP_CONTEXTUAL,IntentPriority.OPEN_LOOP_CONTINUATION,IntentPriority.FALLBACK]
PRIORITY_RANK={v:i for i,v in enumerate(PRIORITY_ORDER)}

@dataclass(frozen=True)
class IntentArbitrationDecision:
    selected_intent:str
    explicit_intent:str
    contextual_intent:str
    reason:str
    confidence:float
    open_loop_overridden:bool
    context_topic:Optional[str]=None

def _n(s:str)->str:
    return (s or "").strip().lower()

def classify_explicit_intent(message:str)->IntentPriority:
    t=_n(message)
    rules=[
        (IntentPriority.CALCULATION, r"(\d+\s*[\+\-\*x×/]\s*\d+)|(\bquanto\b.*\d+)|\bcalcule\b"),
        (IntentPriority.TASK_EXECUTION, r"\b(busque|procure|execute|rode|faça|faca|crie|gere|salve|corrija|implante)\b"),
        (IntentPriority.VERIFICATION, r"\b(verifique|valide|confirme|cheque|audite|teste)\b"),
        (IntentPriority.ANALYSIS, r"\b(analise|compare|diagnostique|explique|por que|porque|causa raiz)\b"),
        (IntentPriority.TROUBLESHOOTING, r"\b(erro|falha|bug|quebrou|deu errado|problema|não funciona|nao funciona|travou)\b"),
        (IntentPriority.SOCIAL, r"\b(oi|olá|ola|bom dia|boa tarde|boa noite|tudo bem|quem é vc|quem e vc|quem é você|quem e voce|como vc está|como vc esta)\b"),
        (IntentPriority.FOLLOWUP_CONTEXTUAL, r"^(aprofunde|detalhe|explique melhor|continue|prossiga|mais detalhes|desenvolva)$"),
        (IntentPriority.OPEN_LOOP_CONTINUATION, r"^(e depois\??|depois\??|próximo|proximo|então\??|entao\??|ok e agora\??)$"),
    ]
    for intent,pat in rules:
        if re.search(pat,t):
            return intent
    return IntentPriority.FALLBACK

def arbitrate_intent_priority(message:str, context:Optional[Dict[str,Any]]=None, contextual_intent:Optional[str]=None)->IntentArbitrationDecision:
    ctx=context or {}
    explicit=classify_explicit_intent(message)
    ctx_intent=IntentPriority(contextual_intent) if contextual_intent in IntentPriority._value2member_map_ else (IntentPriority.OPEN_LOOP_CONTINUATION if ctx.get("last_topic") else IntentPriority.FALLBACK)
    selected=explicit if PRIORITY_RANK[explicit] <= PRIORITY_RANK[ctx_intent] else ctx_intent
    overridden=ctx_intent==IntentPriority.OPEN_LOOP_CONTINUATION and explicit not in (IntentPriority.OPEN_LOOP_CONTINUATION,IntentPriority.FALLBACK)
    return IntentArbitrationDecision(selected.value,explicit.value,ctx_intent.value,"explicit_intent_priority" if overridden else "priority_rank",0.95 if explicit!=IntentPriority.FALLBACK else 0.55,overridden,ctx.get("last_topic"))

def decision_to_dict(d:IntentArbitrationDecision)->Dict[str,Any]:
    return asdict(d)

def classify_intent(message: str):
    """Public SSA adapter: exposes IAPE intent classification without response patching."""
    return classify_explicit_intent(message)

