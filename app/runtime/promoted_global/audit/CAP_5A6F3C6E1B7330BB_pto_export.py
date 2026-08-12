import os,json,datetime,shutil,subprocess
from pathlib import Path
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

folder=Path("TRANSFER_PACKAGE")/("PTO_"+datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ"))
folder.mkdir(parents=True,exist_ok=True)

snap=ExecutiveSnapshot().build()

audit={
 "mission":"PTO_MIND_RODEIO_TRANSFER_PACKAGE",
 "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
 "repo":"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core",
 "latest_confirmed_counts":snap["counts"],
 "critical_gaps":snap.get("critical_gaps"),
 "last_major_result":{
   "P5.6E2_MASTER_GENETIC_EXPANSION":{
     "animals":"32 -> 63",
     "pedigree_edges":"7 -> 36",
     "valuation_events":"110 -> 141",
     "audit_logs":"2291 -> 3329",
     "reproduction_records":"6 -> 6"
   }
 },
 "known_blockers":[
   "SERPAPI_HTTP_429_RATE_LIMIT",
   "YouTube bot/sign-in blocking solved parcialmente com cookies",
   "p56e2_master_genetic_expansion.py não existia antes; foi criado manualmente",
   "p55a_media não possui evidence_hash nem raw_payload",
   "reproduction_records ainda baixo"
 ]
}

(folder/"PTO_EXECUTION_AUDIT.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2,default=str),encoding="utf-8")

prompt=f"""[PTO — CONTINUIDADE MIND RODEIO]

Você está assumindo o projeto MIND Rodeio no repo:
C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core

NÃO invente dados. Use somente evidências, comandos e snapshots reais.

STATUS CONFIRMADO:
{json.dumps(audit,ensure_ascii=False,indent=2,default=str)}

MÓDULOS RELEVANTES EXISTENTES:
- p5_5u_real_result_claim_extractor
- p5_5v_pedigree_extractor
- p5_5x_genetic_graph_builder
- p5_6c_pedigree_source_validation
- p5_6d_market_valuation_real_prices
- p5_6f1_animal_discovery_engine
- p5_6b4/b5/b6 vídeo/biomecânica/valuation

PRÓXIMA MISSÃO:
1. Auditar p56e2_master_genetic_expansion_audit.json.
2. Validar se os 31 animais novos são reais ou lixo semântico.
3. Deduplicar/limpar animais falsos.
4. Converter pedigree_edges em reproduction_records.
5. Recalcular genetic graph.
6. Gerar snapshot final.
"""

(folder/"PTO_NEXT_CHAT_PROMPT.md").write_text(prompt,encoding="utf-8")

for f in Path(".").glob("p56*.json"):
    shutil.copy2(f, folder/f.name)
for f in Path(".").glob("p56*.py"):
    shutil.copy2(f, folder/f.name)

print(json.dumps({"PTO_EXPORT_DONE":True,"folder":str(folder),"files":len(list(folder.iterdir()))},indent=2,ensure_ascii=False))

remote=os.getenv("RCLONE_REMOTE","gdrive")
drive_folder_id="1fSg7rryuF1RLUX5Hgz9dxEFPTtcBuMfC"
try:
    subprocess.run(["rclone","copy",str(folder),f"{remote}:","--drive-root-folder-id",drive_folder_id,"--progress"],check=True)
    print("DRIVE_UPLOAD_DONE")
except Exception as e:
    print("DRIVE_UPLOAD_NOT_CONFIRMED:",str(e))
    print("Faça upload manual da pasta:",folder)
