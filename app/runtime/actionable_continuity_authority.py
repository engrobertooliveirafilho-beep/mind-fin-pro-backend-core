from __future__ import annotations

def _aca_trace(event_name, **kwargs):
    try:
        print("ACA_TRACE|" + event_name + "|" + repr(kwargs))
    except Exception:
        pass



import ast
import operator as op
import re
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

_CURRENT_TURN: ContextVar[dict[str, Any]] = ContextVar("actionable_turn", default={})

FORBIDDEN_FRAGMENTS = [
    "Memória contextual",
    "vou manter a continuidade",
    "Pode mandar a dúvida direto",
    "Entendi. Vou tratar isso como tarefa",
    "sem puxar contexto antigo",
    "responder pelo que você acabou de falar",
    "como posso ajudar hoje",
]

INTENT_PATTERNS = {
    "detalhar": [r"\bdetalh", r"mais detalhes", r"detalhar mais"],
    "aprofundar": [r"\baprofund"],
    "continuar": [r"\be depois\b", r"\bdepois\b", r"\bcontinua", r"\bpróximo\b", r"\bsegue\b"],
    "responder_agora": [r"\bent[aã]o responda\b", r"\bresponda agora\b", r"\bresponde\b", r"\bent[aã]o\b"],
    "calcular": [r"\bcalcule\b", r"\bquanto [ée]\b", r"\d+\s*[\+\-\*/x]\s*\d+"],
    "analisar": [r"\banalis"],
    "verificar": [r"\bverifi", r"\bche", r"\bvalid", r"implanta[cç][oõ]es", r"problema"],
    "comparar": [r"\bcompar"],
    "planejar": [r"\bplanej"],
    "executar": [r"\bexecut"],
    "resumir": [r"\bresum"],
    "auditar": [r"\baudit"],
}

_SAFE_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

@dataclass
class ContinuityState:
    active_topic: str = ""
    last_open_task: str = ""
    last_reply: str = ""
    conversation_summary: str = ""

def set_actionable_turn_context(sender_id: str, user_message: str, last_state: dict[str, Any] | None = None) -> None:
    _CURRENT_TURN.set({"sender_id": sender_id or "", "user_message": user_message or "", "last_state": last_state or {}})

def _norm(s: str) -> str:
    return (s or "").strip()

def _state(last_state: dict[str, Any] | None) -> ContinuityState:
    d = last_state or {}
    return ContinuityState(
        active_topic=_norm(d.get("active_topic") or d.get("topic") or d.get("last_topic") or d.get("current_topic") or ""),
        last_open_task=_norm(d.get("last_open_task") or d.get("open_task") or d.get("task") or ""),
        last_reply=_norm(d.get("last_reply") or d.get("assistant_last_reply") or d.get("reply") or ""),
        conversation_summary=_norm(d.get("conversation_summary") or d.get("summary") or ""),
    )

def detect_intent(user_message: str) -> str:
    msg = (user_message or "").lower()
    for intent, pats in INTENT_PATTERNS.items():
        if any(re.search(p, msg, re.I) for p in pats):
            return intent
    return "responder_agora" if len(msg.split()) <= 4 else "analisar"

def _safe_eval_expr(expr: str) -> float | int | None:
    expr = expr.lower().replace("mais", "+").replace("menos", "-").replace("vezes", "*").replace("x", "*").replace(",", ".")
    expr = re.sub(r"[^0-9\.\+\-\*/\(\)% ]", "", expr).strip()
    if not expr:
        return None
    expr = expr.replace("%", "/100")
    node = ast.parse(expr, mode="eval")
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _SAFE_OPS: return _SAFE_OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _SAFE_OPS: return _SAFE_OPS[type(n.op)](ev(n.operand))
        raise ValueError("unsafe")
    out = ev(node)
    return int(out) if isinstance(out, float) and out.is_integer() else out

def _calc(user_message: str) -> str | None:
    try:
        result = _safe_eval_expr(user_message)
        if result is not None:
            return f"Resultado: {result}."
    except Exception:
        return "Não consegui calcular com segurança. Envie só a expressão numérica."
    return None

def _basis(s: ContinuityState, user_message: str) -> str:
    return s.last_open_task or s.active_topic or s.conversation_summary or s.last_reply or user_message

def _has_forbidden(reply: str) -> bool:
    low = reply or ""
    return any(f.lower() in low.lower() for f in FORBIDDEN_FRAGMENTS)

def resolve_actionable_followup(sender_id: str, user_message: str, last_state: dict[str, Any] | None = None) -> str:
    s = _state(last_state)
    intent = detect_intent(user_message)
    base = _basis(s, user_message)

    if intent == "calcular":
        return _calc(user_message) or "Cálculo: envie a expressão objetiva para eu retornar o resultado."

    if intent in ("detalhar", "aprofundar"):
        return f"Detalhamento: {base}. Pontos-chave: 1) causa provável, 2) impacto prático, 3) próxima validação objetiva."

    if intent == "continuar":
        return f"Próximo passo: continuar em {base}. Execute a validação, registre evidência e só avance se o resultado estiver verde."

    if intent == "responder_agora":
        return f"Resposta direta: {base}. Ação recomendada: validar no caminho real, eliminar placeholder e registrar evidência."

    if intent == "verificar":
        return f"Verificação: 1) confirmar entrada real, 2) checar rota/camada final, 3) validar saída, 4) registrar log, 5) bloquear falso positivo."

    if intent == "analisar":
        return f"Análise: contexto={base}. Diagnóstico: falta evidência completa. Risco: falso verde. Ação: testar fluxo real e salvar relatório."

    if intent == "comparar":
        return f"Comparação: avalie {base} por impacto, risco, custo de correção e evidência disponível. Priorize o maior risco live."

    if intent == "planejar":
        return f"Plano: 1) isolar fluxo real, 2) corrigir último hop, 3) testar local, 4) validar live, 5) exportar evidências."

    if intent == "executar":
        return f"Execução: aplique correção no caminho real, rode py_compile/pytest, valide /version, teste webhook e exporte JSONs."

    if intent == "resumir":
        return f"Resumo: {base}. Status: exige validação objetiva antes de declarar fechamento."

    if intent == "auditar":
        return f"Auditoria: verifique placeholders, duplicação, fallback fraco, resposta vaga, sync Render, teste live e evidência Drive."

    return f"Resposta direta: {base}."

def guard_actionable_reply(reply: str, sender_id: str = "", user_message: str = "", last_state: dict[str, Any] | None = None) -> str:
    _aca_trace(
        "ENTER",
        user_message=user_message,
        reply_before=reply
    )

    turn = _CURRENT_TURN.get() or {}
    sid = sender_id or turn.get("sender_id", "")
    msg = user_message or turn.get("user_message", "")
    st = last_state or turn.get("last_state", {})
    intent = detect_intent(msg)

    if is_small_talk(msg):
        return natural_small_talk(msg)
    _aca_trace("INTENT", detected=intent, user_message=msg)

    weak = not reply or len(reply.strip()) < 12 or _has_forbidden(reply)
    actionable_intent = intent in set(INTENT_PATTERNS.keys())
    if weak:
        candidate = resolve_actionable_followup(sid, msg, st)
        if candidate and not _has_forbidden(candidate):
            
            _aca_trace(
                "REWRITE",
                intent=intent,
                before=reply,
                after=candidate
            )
            return candidate

    
    _aca_trace(
        "BYPASS",
        intent=intent if "intent" in locals() else None,
        reply_after=reply
    )
    return reply


SMALL_TALK_PATTERNS = [
    "oi","ola","olá","bom dia","boa tarde","boa noite",
    "tudo bem","como vai","e ai","e aí","opa","blz",
    "beleza","tranquilo","suave","fala","hello","hi"
]

def is_small_talk(msg: str) -> bool:
    m = (msg or "").strip().lower()
    return any(x in m for x in SMALL_TALK_PATTERNS)

def natural_small_talk(msg: str) -> str:
    m = (msg or "").lower()

    if "bom dia" in m:
        return "Bom dia! Tudo certo por aí?"
    if "boa tarde" in m:
        return "Boa tarde! Como você está?"
    if "boa noite" in m:
        return "Boa noite! Como foi seu dia?"
    if "tudo bem" in m:
        return "Tudo certo por aqui. E com você?"
    return "Oi! O que você precisa?"

