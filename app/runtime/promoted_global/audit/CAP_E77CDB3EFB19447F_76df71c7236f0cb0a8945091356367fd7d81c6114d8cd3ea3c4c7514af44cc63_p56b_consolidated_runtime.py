import json, requests, os, datetime
from app.mind.p5_6b4_youtube_acquisition_engine.engine import YouTubeAcquisitionEngine
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Prefer":"count=exact"}

def count(table):
    r=requests.get(f"{u}/rest/v1/{table}?select=id&limit=1",headers=h)
    return int((r.headers.get("content-range") or "0-0/0").split("/")[-1])

before={t:count(t) for t in [
    "p55a_media","p55a_biomechanics","p55a_judge_scores",
    "p55a_valuation_events","p55a_audit_logs"
]}

b4=[]
for i in range(1,4):
    try:
        b4.append(YouTubeAcquisitionEngine().run_once(20))
    except Exception as e:
        b4.append({"status":"ERROR","cycle":i,"error":str(e)})

b5=JudgeRealBiomechanicsBinder().run_once(1000)
b6=RealValuationBinder().run_once()

after={t:count(t) for t in before}
snap=ExecutiveSnapshot().build()

audit={
    "mission":"P5.6B4_B5_B6_CONSOLIDATED_RUNTIME",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "before":before,
    "b4_cycles":b4,
    "b5":b5,
    "b6_top":b6.get("top",[])[:10],
    "after":after,
    "growth":{k:after[k]-before[k] for k in before},
    "snapshot_counts":snap["counts"],
    "critical_gaps":snap.get("critical_gaps")
}

open("p56b_consolidated_runtime_audit.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2,default=str))

print(json.dumps({
    "mission":audit["mission"],
    "before":before,
    "after":after,
    "growth":audit["growth"],
    "b5_written":b5.get("judge_scores_written"),
    "b6_animals_scored":b6.get("animals_scored"),
    "critical_gaps":audit["critical_gaps"]
},indent=2,ensure_ascii=False))
