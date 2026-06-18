import os, json, urllib.request, urllib.parse

def mind_bull_score(b):
    base = (
        float(b.get("difficulty_score") or 0) * 0.30 +
        float(b.get("buckoff_pressure_score") or 0) * 0.25 +
        float(b.get("explosiveness_score") or 0) * 0.20 +
        float(b.get("kick_score") or 0) * 0.15 +
        float(b.get("spin_score") or 0) * 0.10
    )
    return round(min(50, max(0, base / 2)), 4)

def score_error(official, mind):
    if official is None:
        return {"absolute_error": None, "percentage_error": None}
    err = abs(float(official) - float(mind))
    return {"absolute_error": round(err, 4), "percentage_error": round((err / max(float(official), 1)) * 100, 4)}

class DigitalJudgeScoreEngine:
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

    def biomechanics_rows(self):
        return self.req("GET","/rest/v1/p55a_biomechanics?select=id,media_id,animal_id,difficulty_score,buckoff_pressure_score,explosiveness_score,kick_score,spin_score,biomechanics_score&limit=100")

    def media_official_score(self, media_id):
        q=urllib.parse.quote(media_id)
        rows=self.req("GET",f"/rest/v1/p55a_media?id=eq.{q}&select=bull_score")
        return rows[0].get("bull_score") if rows else None

    def existing_by_media(self, media_id):
        q=urllib.parse.quote(media_id)
        rows=self.req("GET",f"/rest/v1/p55a_judge_scores?media_id=eq.{q}&select=id,media_id,animal_id,mind_bull_score,official_bull_score")
        return rows[0] if rows else None

    def insert_for_biomechanics(self, b):
        existing=self.existing_by_media(b["media_id"])
        if existing:
            return existing

        official = self.media_official_score(b["media_id"])
        mind = mind_bull_score(b)
        err = score_error(official, mind)

        payload = {
            "media_id": b["media_id"],
            "animal_id": b["animal_id"],
            "official_bull_score": official,
            "mind_bull_score": mind,
            "absolute_error": err["absolute_error"],
            "percentage_error": err["percentage_error"],
            "explanation": {
                "model": "P5.5J.rule_based.v1",
                "inputs": {
                    "difficulty_score": b.get("difficulty_score"),
                    "buckoff_pressure_score": b.get("buckoff_pressure_score"),
                    "explosiveness_score": b.get("explosiveness_score"),
                    "kick_score": b.get("kick_score"),
                    "spin_score": b.get("spin_score")
                },
                "note": "Initial rule-based judge. Replace with trained model when official labeled data grows."
            },
            "model_version": "P5.5J.rule_based.v1",
            "confidence_score": 35
        }
        return self.req("POST","/rest/v1/p55a_judge_scores",payload)[0]

    def seed(self):
        return [self.insert_for_biomechanics(b) for b in self.biomechanics_rows()]

    def audit(self, rows):
        return {
            "status": "P5.5J_DIGITAL_JUDGE_SCORED",
            "total": len(rows),
            "unique_media": len(set(r["media_id"] for r in rows)),
            "ids": [r["id"] for r in rows]
        }
