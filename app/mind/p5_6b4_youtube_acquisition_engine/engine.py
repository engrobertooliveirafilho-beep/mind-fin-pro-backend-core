import os, json, urllib.request, urllib.parse, subprocess, uuid
from pathlib import Path
from app.mind.p5_6b2_real_cv_pipeline.pipeline import analyze_video_file, composite

CACHE = Path("runtime/p56b4_video_cache")

BLOCK_TITLE_TERMS = ["documentary","history","interview","podcast","full event","full ridepass","compilation","highlights","recap","championship round","finals"]
MAX_DURATION_SECONDS = 300

ALLOWED_METRIC_FIELDS = [
    "jump_height","jump_length","horizontal_velocity","vertical_velocity","acceleration",
    "initial_explosion","air_time","kick_frequency","kick_amplitude","direction_changes",
    "angular_velocity","estimated_torque","estimated_kinetic_energy","estimated_power",
    "unpredictability","sporting_aggressiveness","consistency","difficulty"
]

def blocked_title(title):
    t=str(title or "").lower()
    return any(x in t for x in BLOCK_TITLE_TERMS)

class YouTubeAcquisitionEngine:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(
            self.url+path,
            data=data,
            headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},
            method=method
        )
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def youtube_media(self, limit=10):
        rows=self.req("GET",f"/rest/v1/p55a_media?platform=eq.youtube&select=id,animal_id,url,title&limit={limit*10}")
        return [
            r for r in rows
            if ("youtube.com/watch" in r.get("url","").lower() and "v=" in r.get("url","").lower())
            or ("youtu.be/" in r.get("url","").lower())
        ][:limit]

    def video_probe(self, media_url):
        cmd=["yt-dlp","--dump-json","--no-playlist",media_url]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
        if p.returncode != 0:
            raise RuntimeError(("yt-dlp probe failed: "+(p.stderr or p.stdout or ""))[:1000])
        data=json.loads(p.stdout)
        return {"title":data.get("title"),"duration":data.get("duration"),"webpage_url":data.get("webpage_url")}

    def should_skip_media(self, media):
        probe=self.video_probe(media["url"])
        duration=probe.get("duration") or 0
        title=probe.get("title") or media.get("title") or ""
        if blocked_title(title):
            return True, "blocked_title", probe
        if duration and duration > MAX_DURATION_SECONDS:
            return True, f"duration_gt_{MAX_DURATION_SECONDS}", probe
        return False, "allowed", probe

    def download_temp(self, media_url):
        CACHE.mkdir(parents=True,exist_ok=True)
        out=CACHE / f"{uuid.uuid4()}.mp4"
        cmd=[
            "yt-dlp","--no-playlist","--no-warnings","--merge-output-format","mp4",
            "-f","18/best[height<=360]/best",
            "-o",str(out),
            media_url
        ]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
        if p.returncode != 0:
            raise RuntimeError(("yt-dlp failed: "+(p.stderr or p.stdout or ""))[:1500])
        if not out.exists() or out.stat().st_size <= 0:
            raise RuntimeError("yt-dlp did not create output file")
        return out

    def replace_biomechanics(self, media, scores, metrics):
        q=urllib.parse.quote(media["id"])
        old=self.req("GET",f"/rest/v1/p55a_biomechanics?media_id=eq.{q}&select=id")
        for r in old:
            self.req("DELETE",f"/rest/v1/p55a_biomechanics?id=eq.{r['id']}")

        allowed={k:metrics[k] for k in ALLOWED_METRIC_FIELDS if k in metrics}
        payload={
            **allowed,
            **scores,
            "media_id":media["id"],
            "animal_id":media["animal_id"],
            "model_version":"P5.6B4A.filtered_ytdlp_opencv_real.v1",
            "confidence_score":60
        }
        return self.req("POST","/rest/v1/p55a_biomechanics",payload)[0]

    def process_one(self, media):
        path=None
        try:
            skip, reason, probe = self.should_skip_media(media)
            if skip:
                return {"media_id":media["id"],"status":"skipped","reason":reason,"probe":probe}
            path=self.download_temp(media["url"])
            metrics=analyze_video_file(path)
            scores=composite(metrics)
            row=self.replace_biomechanics(media,scores,metrics)
            return {"media_id":media["id"],"status":"processed","biomechanics_id":row["id"],"scores":scores}
        except Exception as e:
            return {"media_id":media["id"],"status":"failed","error":str(e)[:1000]}
        finally:
            if path and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass

    def run_once(self, limit=3):
        rows=self.youtube_media(limit)
        results=[self.process_one(m) for m in rows]
        return {
            "status":"P5.6B4_YOUTUBE_ACQUISITION_ENGINE_DONE",
            "media_scanned":len(rows),
            "processed":sum(1 for r in results if r["status"]=="processed"),
            "failed":sum(1 for r in results if r["status"]=="failed"),
            "skipped":sum(1 for r in results if r["status"]=="skipped"),
            "results":results
        }
