import os, json, urllib.request

class JudgeRealBiomechanicsBinder:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def real_biomechanics(self, limit=500):
        return self.req("GET",f"/rest/v1/p55a_biomechanics?select=id,media_id,animal_id,kick_score,spin_score,difficulty_score,explosiveness_score,buckoff_pressure_score,biomechanics_score,model_version&order=created_at.desc&limit={limit}")

    def score(self, b):
        kick=float(b.get("kick_score") or 0)
        spin=float(b.get("spin_score") or 0)
        diff=float(b.get("difficulty_score") or 0)
        expl=float(b.get("explosiveness_score") or 0)
        buck=float(b.get("buckoff_pressure_score") or 0)
        raw=(kick*.25)+(spin*.18)+(diff*.25)+(expl*.12)+(buck*.20)
        return round(min(50, max(0, raw/2)), 4)

    def replace_judge(self, b):
        old=self.req("GET",f"/rest/v1/p55a_judge_scores?media_id=eq.{b['media_id']}&select=id")
        for r in old:
            self.req("DELETE",f"/rest/v1/p55a_judge_scores?id=eq.{r['id']}")
        payload={
            "media_id":b["media_id"],
            "animal_id":b["animal_id"],
            "official_bull_score":None,
            "mind_bull_score":self.score(b),
            "absolute_error":None,
            "percentage_error":None,
            "explanation":{
                "model":"P5.6B5.real_biomechanics_judge.v1",
                "source_biomechanics_id":b["id"],
                "source_model_version":b.get("model_version"),
                "inputs":{
                    "kick_score":b.get("kick_score"),
                    "spin_score":b.get("spin_score"),
                    "difficulty_score":b.get("difficulty_score"),
                    "explosiveness_score":b.get("explosiveness_score"),
                    "buckoff_pressure_score":b.get("buckoff_pressure_score"),
                    "biomechanics_score":b.get("biomechanics_score")
                }
            },
            "model_version":"P5.6B5.real_biomechanics_judge.v1",
            "confidence_score":55
        }
        return self.req("POST","/rest/v1/p55a_judge_scores",payload)[0]

    def run_once(self, limit=500):
        rows=self.real_biomechanics(limit)
        written=[self.replace_judge(b) for b in rows if b.get("media_id") and b.get("animal_id")]
        return {"status":"P5.6B5_JUDGE_REAL_BIOMECHANICS_BINDER_DONE","biomechanics_scanned":len(rows),"judge_scores_written":len(written),"next_action":"RERUN_VALUATION"}
