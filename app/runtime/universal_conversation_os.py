
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
import ast, operator, re

def _semantic_recall_context(sender_id, msg, top_k=3):
    try:
        from app.eldora.core.semantic_memory_engine import semantic_memory_recall
        data = semantic_memory_recall(sender_id or "default", msg or "", top_k)
        rows = data.get("results", []) if isinstance(data, dict) else []
        try:
            from app.runtime.contextual_reranker import rerank_memories
            ranked = rerank_memories(msg or "", rows, top_k)
        except Exception:
            ranked = rows[:top_k]
        memories = []
        for r in ranked:
            m = str(r.get("message") or "").strip() if isinstance(r, dict) else str(r).strip()
            if m and m.lower() != str(msg or "").lower().strip():
                memories.append(m[:500])
        return {
            "ok": True,
            "backend": "pgvector_reranked",
            "count": len(memories),
            "memories": memories[:top_k],
            "reranked": True,
        }
    except Exception as e:
        return {"ok": False, "backend": "unavailable", "count": 0, "memories": [], "error": str(e)[:160]}


def _persist_semantic_memory(sender_id, user_msg, assistant_reply):
    try:
        from app.eldora.core.semantic_memory_engine import insert_embedding

        sender_id = sender_id or "default"

        payload = (
            f"USER: {str(user_msg or '').strip()}\n"
            f"ELDORA: {str(assistant_reply or '').strip()}"
        ).strip()

        if len(payload) > 8:
            insert_embedding(
                sender_id=sender_id,
                text=payload[:4000],
                metadata={"source":"runtime_auto_ingestion"}
            )

        return {"ok": True}

    except Exception as e:
        return {"ok": False, "error": str(e)[:180]}

def _semantic_candidate_reply(msg, semantic_ctx):

    low = (msg or "").lower()
    joined = "\n".join(semantic_ctx.get("memories", []))
    jlow = joined.lower()
    if not semantic_ctx.get("memories"):
        return ""
    import re, unicodedata
    norm = unicodedata.normalize("NFKD", low).encode("ascii","ignore").decode("ascii")
    jnorm = unicodedata.normalize("NFKD", jlow).encode("ascii","ignore").decode("ascii")
    if any(x in norm for x in ["qual meu nome", "qual e meu nome", "como eu me chamo"]):
        m = re.search(r"meu nome (?:e|eh|é)\s+([A-Za-zÀ-ÿ]+)", jnorm, re.I)
        if m:
            return f"Seu nome é {m.group(1).capitalize()}."
    if any(x in norm for x in ["o que estou estudando", "o que eu estudo", "estou estudando o que"]):
        m = re.search(r"estudando\s+([A-Za-zÀ-ÿ0-9 ]+)", jnorm, re.I)
        if m:
            val=m.group(1).strip().split(".")[0].strip()
            return f"Você está estudando {val}."
    return ""

class ConversationMode(str, Enum):
    SOCIAL="SOCIAL"; TASK="TASK"; FOLLOWUP="FOLLOWUP"; EXECUTION="EXECUTION"; ANALYSIS="ANALYSIS"; CALCULATION="CALCULATION"; VERIFICATION="VERIFICATION"; CLARIFICATION="CLARIFICATION"; EMOTIONAL_SAFE="EMOTIONAL_SAFE"; CLOSURE="CLOSURE"

FORBIDDEN=["Entendi. Me diga melhor","Resposta direta:","Ação recomendada:","Memória contextual:","Vou manter continuidade","Pode mandar a dúvida direto","Como posso ajudar hoje?","Resumo / compatibility","risk:","compatibility:","Diagnóstico:","Estratégia:","Execução:","Auditoria:","Detalhamento:","Pontos-chave:","Análise: contexto="]

@dataclass
class SenderState:
    sender_id:str
    last_user_message:str=""
    last_assistant_reply:str=""
    last_topic:str=""
    last_task:str=""
    last_mode:str=""
    last_intent:str=""
    last_entities:List[str]=field(default_factory=list)
    last_emotional_tone:str="neutral"
    conversation_depth:int=0
    open_loop:str=""
    last_action_plan:List[str]=field(default_factory=list)
    updated_at:str=""

class SenderStateMemory:
    _mem:Dict[str,SenderState]={}
    @classmethod
    def load(cls,sender_id:Optional[str])->SenderState:
        sid=(sender_id or "anonymous").strip()
        return cls._mem.get(sid) or SenderState(sender_id=sid)
    @classmethod
    def save(cls,state:SenderState)->None:
        state.updated_at=datetime.now(timezone.utc).isoformat()
        cls._mem[state.sender_id]=state

class SafeCalculator:
    OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow,ast.USub:operator.neg}
    @classmethod
    def eval_expr(cls,msg:str):
        expr=(msg or "").lower().replace("x","*").replace(",",".")
        expr=re.sub(r"[^0-9\.\+\-\*\/\(\) ]"," ",expr).strip()
        if not re.search(r"\d+\s*[\+\-\*\/]\s*\d+",expr): return None
        return cls._eval(ast.parse(expr,mode="eval").body)
    @classmethod
    def _eval(cls,node):
        if isinstance(node,ast.Num): return node.n
        if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)): return node.value
        if isinstance(node,ast.BinOp): return cls.OPS[type(node.op)](cls._eval(node.left),cls._eval(node.right))
        if isinstance(node,ast.UnaryOp): return cls.OPS[type(node.op)](cls._eval(node.operand))
        raise ValueError("unsafe")


def _process_multiline_message(cls, msg, sender_id=None, candidate_reply=""):
    lines=[x.strip() for x in str(msg or "").splitlines() if x.strip()]
    if len(lines) <= 1:
        return None
    replies=[]
    for line in lines[:5]:
        r=cls.process(line,sender_id,candidate_reply="")
        ans=str(r.get("reply","")).strip() if isinstance(r,dict) else ""
        if ans and ans not in replies:
            replies.append(ans)
    if not replies:
        return None
    return {
        "reply":"\n".join(replies),
        "mode":"MULTILINE",
        "topic":msg,
        "state":{},
        "memory_backend":"multiline_delegated",
        "semantic_recall":{"ok":True,"backend":"line_delegation","count":len(replies)}
    }

class UniversalConversationOS:
    SOCIAL={"oi","oie","ola","olá","fala","salve","bom","boa","dia","tarde","noite","bem","vai","vc","você","ta","tá","esta","está"}
    EXEC={"faça","faz","execute","rode","implante","corrija","crie","gere","salve","commit","push","deploy","busque","procure"}
    ANALYSIS={"analise","analisa","interprete","revise","leia","lê","documento","contrato","imagem","foto","arquivo","texto"}
    VERIFY={"verifique","verifica","confere","audite","audita","valide","valida","teste","testa","problema","erro","falha","bug"}
    FOLLOW={"detalhe","detalha","aprofunda","aprofundar","continua","continue","depois","melhor","novamente","mesmo","explica"}
    EMO={"travou","ferrou","perdido","preocupado","nervoso","ansioso","frustrado","ruim","quebrou","falhou"}

    @classmethod
    def _tokens(cls,msg): return set(re.findall(r"[\wÀ-ÿ]+",(msg or "").lower()))
    @classmethod
    def classify(cls,msg,state):
        low=(msg or "").lower(); toks=cls._tokens(msg)
        if SafeCalculator.eval_expr(low) is not None or any(x in low for x in ["calcula","calcule","quanto dá","quanto da","soma"]): return ConversationMode.CALCULATION
        if toks & cls.ANALYSIS: return ConversationMode.ANALYSIS
        if toks & cls.EXEC: return ConversationMode.EXECUTION
        if toks & cls.VERIFY: return ConversationMode.VERIFICATION
        if toks & cls.EMO: return ConversationMode.EMOTIONAL_SAFE
        if toks & cls.FOLLOW or (len(toks)<=4 and (state.last_topic or state.last_task)): return ConversationMode.FOLLOWUP
        if len(toks)<=6 and len(toks & cls.SOCIAL)>=max(1,len(toks)//2): return ConversationMode.SOCIAL
        if low.endswith("?") and len(toks)<=3 and not state.last_topic: return ConversationMode.CLARIFICATION
        return ConversationMode.TASK

    @classmethod
    def process(cls,msg,sender_id=None,candidate_reply=""):
        multiline=_process_multiline_message(cls,msg,sender_id,candidate_reply)
        if multiline:
            return multiline
        state=SenderStateMemory.load(sender_id)
        semantic_ctx=_semantic_recall_context(sender_id,msg,3)
        semantic_reply=_semantic_candidate_reply(msg,semantic_ctx)
        if semantic_reply and not candidate_reply:
            candidate_reply=semantic_reply
        mode=cls.classify(msg,state)
        topic=(state.last_task or state.last_topic or state.last_user_message or msg) if mode==ConversationMode.FOLLOWUP else (msg or "").strip()
        calc=SafeCalculator.eval_expr(msg or "")
        if semantic_reply:
            reply=semantic_reply
        elif mode==ConversationMode.SOCIAL: reply="Tudo certo, Roberto. Seguimos firmes."
        elif mode==ConversationMode.CALCULATION: reply=f"Resultado: {int(calc) if calc is not None and calc==int(calc) else calc}." if calc is not None else "Me mande a expressão completa em uma linha."
        elif mode==ConversationMode.FOLLOWUP: reply=f"Vamos aprofundar no mesmo contexto: {topic}. O foco é achar a causa real, separar sintoma de origem e validar o próximo teste sem reiniciar a conversa."
        elif mode==ConversationMode.VERIFICATION: reply="Checklist real: 1) isolar último ponto alterado, 2) rodar teste mínimo, 3) comparar saída esperada vs real, 4) registrar evidência."
        elif mode==ConversationMode.ANALYSIS: reply="Envie o arquivo, imagem ou texto exato para eu analisar sem inferir."
        elif mode==ConversationMode.EXECUTION: reply="Execução: aplicar a ação pedida, validar retorno e bloquear falso positivo."
        elif mode==ConversationMode.EMOTIONAL_SAFE: reply=f"Vamos resolver por partes. No contexto de {topic}, começo isolando o erro e reduzindo o escopo."
        elif mode==ConversationMode.CLARIFICATION: reply="Qual item exato você quer que eu valide agora?"
        else: reply=(candidate_reply or "Próximo passo objetivo: definir entrada, validar saída e registrar evidência.").strip()
        if any(x.lower() in reply.lower() for x in FORBIDDEN):
            reply=f"Vamos seguir de forma direta no contexto de {topic}. O próximo passo é isolar a causa real, testar a hipótese principal e registrar evidência antes de avançar."
        state.conversation_depth+=1; state.last_user_message=msg or ""; state.last_assistant_reply=reply; state.last_mode=mode.value; state.last_intent=mode.value.lower()
        if mode not in [ConversationMode.SOCIAL,ConversationMode.CLARIFICATION]: state.last_topic=topic
        if mode in [ConversationMode.TASK,ConversationMode.EXECUTION,ConversationMode.VERIFICATION,ConversationMode.ANALYSIS]: state.last_task=topic; state.open_loop=topic
        state.last_action_plan=["classificar","resolver continuidade","arbitrar saída final"]; SenderStateMemory.save(state)
        
        _persist_semantic_memory(sender_id,msg,reply)

        return {"reply":reply,
                "mode":mode.value,
                "topic":topic,
                "state":asdict(state),
                "memory_backend":"pgvector_hybrid" if semantic_ctx.get("ok") else "runtime_memory_partial",
                "semantic_recall":semantic_ctx}


def universal_conversation_guard(message:str,sender_id:Optional[str],candidate_reply:str="")->str:
    return UniversalConversationOS.process(message,sender_id,candidate_reply)["reply"]
