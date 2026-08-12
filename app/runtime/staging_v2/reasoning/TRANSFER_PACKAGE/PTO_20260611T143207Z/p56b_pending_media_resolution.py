import os, json, requests, datetime
from app.mind.p5_6b4_youtube_acquisition_engine.engine import YouTubeAcquisitionEngine
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"return=representation"}

media=requests.get(f"{u}/rest/v1/p55a_media?select=id,title,url,animal_id&limit=5000",headers=h).json()
bio=requests.get(f"{u}/rest/v1/p55a_biomechanics?select=media_id&limit=5000",headers=h).json()
done={x["media_id"] for x in bio if x.get("media_id")}
missing=[m for m in media if m["id"] not in done]

engine=YouTubeAcquisitionEngine()
results=[]
for m in missing:
    url=(m.get("url") or "").lower()
    if "youtube.com/watch" not in url and "youtu.be/" not in url:
        results.append({"media_id":m["id"],"title":m.get("title"),"status":"not_youtube","url":m.get("url")})
        continue
    results.append(engine.process_one(m))

b5=JudgeRealBiomechanicsBinder().run_once(1000)
b6=RealValuationBinder().run_once()
snap=ExecutiveSnapshot().build()

audit={
    "mission":"P5.6B4_PENDING_MEDIA_RESOLUTION",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "missing_before":len(missing),
    "results":results,
    "processed":sum(1 for r in results if r.get("status")=="processed"),
    "skipped":sum(1 for r in results if r.get("status")=="skipped"),
    "failed":sum(1 for r in results if r.get("status")=="failed"),
    "not_youtube":sum(1 for r in results if r.get("status")=="not_youtube"),
    "b5":b5,
    "b6_animals_scored":b6.get("animals_scored"),
    "counts":snap["counts"],
    "critical_gaps":snap.get("critical_gaps")
}

open("p56b_pending_media_resolution_audit.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2,default=str))
print(json.dumps({k:audit[k] for k in ["mission","missing_before","processed","skipped","failed","not_youtube","b6_animals_scored","counts","critical_gaps"]},indent=2,ensure_ascii=False,default=str))
