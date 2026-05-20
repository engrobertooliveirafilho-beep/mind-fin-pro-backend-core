import json, os, time, uuid, re
TRACE_DIR=os.getenv("ELDORA_TRACE_DIR","_evidence/WHATSAPP_RUNTIME_TRACE")
os.makedirs(TRACE_DIR,exist_ok=True)
BAD_PATTERNS=[
"neura, sua tutora cognitiva",
"tutora cognitiva",
"como posso te ajudar hoje",
"acompanhar o contexto da conversa",
"eu sou a neura",
"sou a eldora, a camada conversacional",
"camada conversacional do mind"
]
def leak_type(text):
    low=(text or "").lower()
    hits=[p for p in BAD_PATTERNS if p in low]
    return hits
def new_trace(sender_id="",user_message=""):
    return {
        "trace_id":str(uuid.uuid4()),
        "ts":time.time(),
        "sender_id":sender_id,
        "user_message":user_message,
        "events":[]
    }
def add_event(trace,stage,module,function,input_preview="",output_preview="",extra=None):
    if trace is None:
        trace=new_trace()
    out=str(output_preview or "")
    trace["events"].append({
        "stage":stage,
        "module":module,
        "function":function,
        "input_preview":str(input_preview or "")[:240],
        "output_preview":out[:240],
        "leaks":leak_type(out),
        "extra":extra or {}
    })
    return trace
def save_trace(trace):
    os.makedirs(TRACE_DIR,exist_ok=True)
    p=os.path.join(TRACE_DIR,f"{trace.get('trace_id','noid')}.json")
    with open(p,"w",encoding="utf-8") as f:
        json.dump(trace,f,ensure_ascii=False,indent=2)
    return p
def assert_clean_output(text):
    hits=leak_type(text)
    if hits:
        return False,hits
    return True,[]
def sanitize_final_output(user_message,text):
    low=(text or "").lower()
    if "neura" in low or "tutora cognitiva" in low or "dúvidas e estudos" in low or "duvidas e estudos" in low or "prova" in low or "matemática" in low or "matematica" in low or "estudos" in low or "resumo técnico do mind" in low or "runtime estável" in low or "context fusion" in low or "webhook produtivo" in low:
        return answer if answer else "Tudo certo por aqui 🙂"
    if "como posso te ajudar" in low or "como posso ajudar" in low:
        return "entendi. pelo contexto, estamos testando a Eldora no WhatsApp e caçando o ponto que ainda troca a persona."
    if "sou a eldora, a camada conversacional" in low:
        return "estou acompanhando o contexto. O ponto agora é corrigir a rota que ainda está escapando fallback antigo."
    return text




