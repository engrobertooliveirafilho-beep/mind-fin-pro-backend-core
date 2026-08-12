import os,json,requests,datetime
from app.mind.p5_6b4_youtube_acquisition_engine.engine import YouTubeAcquisitionEngine
from app.mind.p5_6b5_judge_real_biomechanics_binder.binder import JudgeRealBiomechanicsBinder
from app.mind.p5_6b6_real_valuation_binder.binder import RealValuationBinder
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

import app.mind.p5_6b4_youtube_acquisition_engine.engine as eng

eng.MAX_DURATION_SECONDS = 900
eng.BLOCK_TITLE_TERMS = ["documentary","history","interview","podcast"]

original_probe = YouTubeAcquisitionEngine.video_probe
original_download = YouTubeAcquisitionEngine.download_temp

def patched_probe(self, media_url):
    import subprocess, json
    cmd=["yt-dlp","--cookies-from-browser","chrome","--dump-json","--no-playlist",media_url]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if p.returncode != 0:
        cmd=["yt-dlp","--cookies-from-browser","edge","--dump-json","--no-playlist",media_url]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if p.returncode != 0:
        return original_probe(self, media_url)
    data=json.loads(p.stdout)
    return {"title":data.get("title"),"duration":data.get("duration"),"webpage_url":data.get("webpage_url")}

def patched_download(self, media_url):
    from pathlib import Path
    import subprocess, uuid
    eng.CACHE.mkdir(parents=True,exist_ok=True)
    out=eng.CACHE / f"{uuid.uuid4()}.mp4"
    base=["yt-dlp","--cookies-from-browser","chrome","--no-playlist","--no-warnings","--merge-output-format","mp4","-f","18/best[height<=360]/best","-o",str(out),media_url]
    p=subprocess.run(base,capture_output=True,text=True,timeout=420)
    if p.returncode != 0:
        base[2]="edge"
        p=subprocess.run(base,capture_output=True,text=True,timeout=420)
    if p.returncode != 0:
        return original_download(self, media_url)
    if not out.exists() or out.stat().st_size <= 0:
        raise RuntimeError("yt-dlp did not create output file")
    return out

YouTubeAcquisitionEngine.video_probe = patched_probe
YouTubeAcquisitionEngine.download_temp = patched_download

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k}

media=requests.get(f"{u}/rest/v1/p55a_media?select=id,title,url,animal_id&platform=eq.youtube&limit=5000",headers=h).json()
bio=requests.get(f"{u}/rest/v1/p55a_biomechanics?select=media_id&limit=5000",headers=h).json()
done={b["media_id"] for b in bio if b.get("media_id")}
pending=[m for m in media if m["id"] not in done and ("youtube.com/watch" in (m.get("url") or "") or "youtu.be/" in (m.get("url") or ""))]

engine=YouTubeAcquisitionEngine()
results=[]
for m in pending[:80]:
    results.append(engine.process_one(m))

b5=JudgeRealBiomechanicsBinder().run_once(1000)
b6=RealValuationBinder().run_once()
snap=ExecutiveSnapshot().build()

audit={
 "mission":"P5.6H_RELAXED_900S_COOKIES_PENDING_MEDIA",
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

open("p56h_relaxed_900s_cookies_pending_media.json","w",encoding="utf-8").write(json.dumps({"audit":audit,"results":results},ensure_ascii=False,indent=2,default=str))
print(json.dumps(audit,indent=2,ensure_ascii=False,default=str))
