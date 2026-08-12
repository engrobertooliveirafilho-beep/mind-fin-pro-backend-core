import os,json,requests,datetime
from app.mind.p5_6b4_youtube_acquisition_engine.engine import YouTubeAcquisitionEngine
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k}

media=requests.get(f"{u}/rest/v1/p55a_media?select=id,title,url,animal_id&platform=eq.youtube&limit=5000",headers=h).json()
bio=requests.get(f"{u}/rest/v1/p55a_biomechanics?select=media_id&limit=5000",headers=h).json()
done={b["media_id"] for b in bio if b.get("media_id")}
pending=[m for m in media if m["id"] not in done and ("youtube.com/watch" in (m.get("url") or "") or "youtu.be/" in (m.get("url") or ""))]

engine=YouTubeAcquisitionEngine()
results=[]
for m in pending[:60]:
    results.append(engine.process_one(m))

b5=JudgeRealBiomechanicsBinder().run_once(1000)
b6=RealValuationBinder().run_once()
snap=ExecutiveSnapshot().build()

audit={
 "mission":"P5.6H_PROCESS_ONLY_PENDING_YOUTUBE_MEDIA",
 "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
 "pending_before":len(pending),
 "attempted":len(results),
 "processed":sum(1 for r in results if r.get("status")=="processed"),
 "skipped":sum(1 for r in results if r.get("status")=="skipped"),
 "failed":sum(1 for r in results if r.get("status")=="failed"),
 "b5_written":b5.get("judge_scores_written"),
 "b6_animals_scored":b6.get("animals_scored"),
 "counts":snap["counts"],
 "critical_gaps":snap.get("critical_gaps")
}

open("p56h_process_only_pending_youtube_media.json","w",encoding="utf-8").write(json.dumps({"audit":audit,"results":results},ensure_ascii=False,indent=2,default=str))
print(json.dumps(audit,indent=2,ensure_ascii=False,default=str))
