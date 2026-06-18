import os, json, urllib.request, urllib.parse

DEFAULT_METRICS = {
    "jump_height": 55,
    "jump_length": 55,
    "horizontal_velocity": 55,
    "vertical_velocity": 55,
    "acceleration": 55,
    "initial_explosion": 60,
    "air_time": 55,
    "kick_frequency": 60,
    "kick_amplitude": 60,
    "direction_changes": 3,
    "angular_velocity": 55,
    "estimated_torque": 55,
    "estimated_kinetic_energy": 55,
    "estimated_power": 55,
    "unpredictability": 60,
    "sporting_aggressiveness": 60,
    "consistency": 50,
    "difficulty": 60
}

def clamp(x):
    return max(0, min(100, float(x or 0)))

def compute_scores(m):
    biomechanics = sum(clamp(v) for v in m.values() if isinstance(v, (int,float))) / len(m)
    return {
        "biomechanics_score": round(clamp(biomechanics), 4),
        "buckoff_pressure_score": round((clamp(m.get("initial_explosion")) + clamp(m.get("unpredictability")) + clamp(m.get("difficulty"))) / 3, 4),
        "explosiveness_score": round(clamp(m.get("initial_explosion")), 4),
        "spin_score": round(clamp(m.get("angular_velocity")), 4),
        "kick_score": round((clamp(m.get("kick_frequency")) + clamp(m.get("kick_amplitude"))) / 2, 4),
        "difficulty_score": round(clamp(m.get("difficulty")), 4),
        "consistency_score": round(clamp(m.get("consistency")), 4)
    }

class BiomechanicsScoreEngine:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            return json.loads(x.read().decode("utf-8"))

    def media_rows(self):
        return self.req("GET","/rest/v1/p55a_media?select=id,animal_id,url,title&limit=25")

    def existing_by_media(self, media_id):
        q=urllib.parse.quote(media_id)
        rows=self.req("GET",f"/rest/v1/p55a_biomechanics?media_id=eq.{q}&select=id,media_id,animal_id,biomechanics_score")
        return rows[0] if rows else None

    def insert_for_media(self, media, metrics=None):
        existing=self.existing_by_media(media["id"])
        if existing:
            return existing
        m=dict(DEFAULT_METRICS)
        if metrics:
            m.update(metrics)
        scores=compute_scores(m)
        payload={**m, **scores, "media_id":media["id"], "animal_id":media["animal_id"], "model_version":"P5.5I.placeholder.v1", "confidence_score":35}
        return self.req("POST","/rest/v1/p55a_biomechanics",payload)[0]

    def seed(self):
        return [self.insert_for_media(m) for m in self.media_rows()]

    def audit(self, rows):
        return {"status":"P5.5I_BIOMECHANICS_SCORED","total":len(rows),"unique_media":len(set(r["media_id"] for r in rows)),"ids":[r["id"] for r in rows]}
