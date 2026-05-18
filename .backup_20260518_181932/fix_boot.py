from pathlib import Path
p=Path("app/memory/provider.py")
txt=p.read_text(encoding="utf-8")
txt=txt.replace('self.database_url=os.getenv("DATABASE_URL")','self.database_url=os.getenv("DATABASE_URL"); assert self.database_url, "DATABASE_URL missing"')
p.write_text(txt,encoding="utf-8")

m=Path("app/main.py")
txt=m.read_text(encoding="utf-8")
if '@app.get("/health")' not in txt:
    txt='''from fastapi import FastAPI, Request, Response\napp=FastAPI()\n@app.get("/health")\ndef health(): return {"status":"ok"}\n@app.get("/version")\ndef version(): return {"status":"ok","service":"mind-fin-pro-backend","runtime":"twilio_retrieval_orchestrator_v1"}\n'''+txt
m.write_text(txt,encoding="utf-8")
print("BOOT_PATCH_OK")
