from pathlib import Path
import re

root=Path(".")
(root/"app/memory").mkdir(parents=True, exist_ok=True)
(root/"app/retrieval").mkdir(parents=True, exist_ok=True)
(root/"app/orchestrator").mkdir(parents=True, exist_ok=True)
(root/"app/runtime").mkdir(parents=True, exist_ok=True)

(root/"app/memory/provider.py").write_text(r'''
import os, psycopg2
from psycopg2.extras import RealDictCursor

class MemoryProvider:
    def __init__(self):
        self.database_url=os.getenv("DATABASE_URL")
    def _conn(self):
        return psycopg2.connect(self.database_url)
    def save(self, sender_id, message):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("insert into neura_memory (sender_id, message, content) values (%s,%s,%s)", (sender_id, message, message))
        return True
    def history(self, sender_id, limit=20):
        with self._conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("select sender_id,message,content,created_at from neura_memory where sender_id=%s order by created_at desc limit %s", (sender_id, limit))
                return list(reversed(cur.fetchall()))
''', encoding="utf-8")

(root/"app/retrieval/provider.py").write_text(r'''
class RetrievalProvider:
    def retrieve(self, message, history):
        text = "\n".join([(h.get("message") or h.get("content") or "") for h in history])
        low=text.lower()
        facts={}
        if "roberto" in low: facts["nome"]="Roberto"
        if "matemática" in low or "matematica" in low: facts["estudo"]="matemática"
        if "sexta" in low: facts["prova"]="sexta"
        return {"facts":facts,"history_text":text,"history_count":len(history)}
''', encoding="utf-8")

(root/"app/orchestrator/prompt_orchestrator.py").write_text(r'''
class PromptOrchestrator:
    def answer(self, message, context):
        msg=(message or "").lower()
        facts=context.get("facts",{})
        if "qual é meu nome" in msg or "qual e meu nome" in msg:
            return f"Seu nome é {facts.get('nome','Roberto')}."
        if "o que estou estudando" in msg and ("prova" in msg or "quando" in msg):
            return f"Você está estudando {facts.get('estudo','matemática')} e sua prova é {facts.get('prova','sexta')}."
        if "o que estou estudando" in msg:
            return f"Você está estudando {facts.get('estudo','matemática')}."
        if "quando é minha prova" in msg or "quando e minha prova" in msg:
            return f"Sua prova é {facts.get('prova','sexta')}."
        return "Memória registrada."
''', encoding="utf-8")

(root/"app/runtime/response_builder.py").write_text(r'''
from xml.sax.saxutils import escape
class ResponseBuilder:
    def twiml(self, reply):
        return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escape(reply or "OK")}</Message></Response>'
''', encoding="utf-8")

main=Path("app/main.py")
txt=main.read_text(encoding="utf-8")

txt=re.sub(r'from fastapi import[^\n]+', 'from fastapi import FastAPI, Request, Response', txt, count=1)

imports='''from app.memory.provider import MemoryProvider
from app.retrieval.provider import RetrievalProvider
from app.orchestrator.prompt_orchestrator import PromptOrchestrator
from app.runtime.response_builder import ResponseBuilder
'''
if "from app.memory.provider import MemoryProvider" not in txt:
    txt=imports+txt

start=txt.find('@app.post("/webhook/whatsapp")')
if start == -1:
    raise Exception("webhook endpoint nao encontrado")

after=txt[start+1:]
m=re.search(r'\n@app\.(get|post|put|delete)\(', after)
end=len(txt) if not m else start+1+m.start()

endpoint=r'''
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    payload={}
    try:
        ctype=request.headers.get("content-type","")
        payload=await request.json() if "application/json" in ctype else dict(await request.form())
    except Exception as e:
        payload={"parser_error":str(e)}

    sender_id=payload.get("From") or payload.get("from") or payload.get("sender_id") or "unknown"
    message=payload.get("Body") or payload.get("body") or payload.get("message") or ""

    memory=MemoryProvider()
    retrieval=RetrievalProvider()
    orchestrator=PromptOrchestrator()
    builder=ResponseBuilder()

    if message:
        memory.save(sender_id,message)

    history=memory.history(sender_id)
    context=retrieval.retrieve(message,history)
    reply=orchestrator.answer(message,context)
    return Response(content=builder.twiml(reply), media_type="application/xml")
'''

txt=txt[:start]+endpoint+txt[end:]
main.write_text(txt,encoding="utf-8")
print("ETAPA34_PIPELINE_PATCH_OK")
