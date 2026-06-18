import os, json, urllib.request, urllib.parse
from datetime import datetime, timezone

def score_from_metadata(media):
    title=(media.get("title") or "").lower()
    base=45
    if "official" in title: base += 5
    if "score" in title: base += 5
    if "pbr" in title: base += 5
    if "youtube" in title: base += 3
    return min(100, base)

class VideoComputerVisionEngine:
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

    def media(self, limit=100):
        return self.req("GET",f"/rest/v1/p55a_media?select=id,animal_id,url,title,platform,metadata,confidence_score&limit={limit}")

    def existing_biomechanics(self, media_id):
        q=urllib.parse.quote(media_id)
        rows=self.req("GET",f"/rest/v1/p55a_biomechanics?media_id=eq.{q}&select=id,media_id")
        return rows[0] if rows else None

    def analyze_media_stub(self, media):
        existing=self.existing_biomechanics(media["id"])
        if existing:
            return {"status":"already_scored","id":existing["id"],"media_id":media["id"]}

        base=score_from_metadata(media)
        metrics={
            "jump_height":base,
            "jump_length":base,
            "horizontal_velocity":base,
            "vertical_velocity":base,
            "acceleration":base,
            "initial_explosion":min(100,base+5),
            "air_time":base,
            "kick_frequency":min(100,base+5),
            "kick_amplitude":min(100,base+5),
            "direction_changes":3,
            "angular_velocity":base,
            "estimated_torque":base,
            "estimated_kinetic_energy":base,
            "estimated_power":base,
            "unpredictability":min(100,base+5),
            "sporting_aggressiveness":min(100,base+5),
            "consistency":max(0,base-5),
            "difficulty":min(100,base+5),
        }
        bio=sum(float(v) for v in metrics.values() if isinstance(v,(int,float))) / len(metrics)
        payload={
            **metrics,
            "media_id":media["id"],
            "animal_id":media["animal_id"],
            "biomechanics_score":round(bio,4),
            "buckoff_pressure_score":round((metrics["initial_explosion"]+metrics["unpredictability"]+metrics["difficulty"])/3,4),
            "explosiveness_score":metrics["initial_explosion"],
            "spin_score":metrics["angular_velocity"],
            "kick_score":round((metrics["kick_frequency"]+metrics["kick_amplitude"])/2,4),
            "difficulty_score":metrics["difficulty"],
            "consistency_score":metrics["consistency"],
            "model_version":"P5.6B.metadata_stub.v1",
            "confidence_score":25
        }
        row=self.req("POST","/rest/v1/p55a_biomechanics",payload)[0]
        return {"status":"created","id":row["id"],"media_id":media["id"]}

    def run_once(self, limit=100):
        rows=self.media(limit)
        results=[self.analyze_media_stub(m) for m in rows]
        created=sum(1 for r in results if r["status"]=="created")
        seen=sum(1 for r in results if r["status"]=="already_scored")
        return {
            "status":"P5.6B_VIDEO_COMPUTER_VISION_ENGINE_DONE",
            "media_scanned":len(rows),
            "biomechanics_created":created,
            "already_scored":seen,
            "mode":"metadata_stub_until_ffmpeg_yolo_pipeline",
            "next_action":"P5.6B2_FFMPEG_YOLO_FRAME_PIPELINE"
        }
