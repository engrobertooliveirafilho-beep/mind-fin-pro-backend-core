import os, json, urllib.request, urllib.parse
from collections import defaultdict

def avg(xs):
    xs=[float(x or 0) for x in xs]
    return round(sum(xs)/len(xs),4) if xs else 0

class RealValuationBinder:
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

    def animals(self):
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name,confidence_score,country,life_status")

    def judges(self):
        return self.req("GET","/rest/v1/p55a_judge_scores?select=animal_id,mind_bull_score,confidence_score,model_version&limit=10000")

    def biomechanics(self):
        return self.req("GET","/rest/v1/p55a_biomechanics?select=animal_id,biomechanics_score,model_version&limit=10000")

    def media(self):
        return self.req("GET","/rest/v1/p55a_media?select=animal_id,id&limit=10000")

    def pedigree(self):
        return self.req("GET","/rest/v1/p55a_pedigree_edges?select=parent_id,child_id&limit=10000")

    def clear_old_real(self, animal_id):
        aid=urllib.parse.quote(animal_id)
        old=self.req("GET",f"/rest/v1/p55a_valuation_events?animal_id=eq.{aid}&event_type=eq.P5.6B6_REAL_VALUATION&select=id")
        for r in old:
            self.req("DELETE",f"/rest/v1/p55a_valuation_events?id=eq.{r['id']}")

    def run_once(self):
        animals=self.animals()
        judge_by=defaultdict(list)
        bio_by=defaultdict(list)
        media_by=defaultdict(int)
        ped_by=defaultdict(int)

        for j in self.judges():
            judge_by[j["animal_id"]].append(j.get("mind_bull_score"))
        for b in self.biomechanics():
            bio_by[b["animal_id"]].append(b.get("biomechanics_score"))
        for m in self.media():
            media_by[m["animal_id"]]+=1
        for e in self.pedigree():
            ped_by[e["parent_id"]]+=1
            ped_by[e["child_id"]]+=1

        written=[]
        for a in animals:
            aid=a["id"]
            avg_j=avg(judge_by[aid])
            avg_b=avg(bio_by[aid])
            media_count=media_by[aid]
            ped_count=ped_by[aid]
            base_conf=float(a.get("confidence_score") or 0)

            amount=round(
                (avg_j*1.25) +
                (avg_b*0.45) +
                min(media_count*1.5,25) +
                min(ped_count*2,20) +
                (base_conf*0.08),
                4
            )

            payload={
                "animal_id":aid,
                "event_type":"P5.6B6_REAL_VALUATION",
                "amount":amount,
                "currency":"SCORE",
                "source_id":None,
                "raw_payload":{
                    "mission":"P5.6B6",
                    "official_name":a.get("official_name"),
                    "avg_judge_score":avg_j,
                    "avg_biomechanics_score":avg_b,
                    "media_count":media_count,
                    "pedigree_edges":ped_count,
                    "confidence":base_conf,
                    "valuation_formula":"judge*1.25 + biomechanics*0.45 + media + pedigree + confidence"
                },
                "confidence_score":60 if media_count and avg_b else 35,
                "validation_status":"provisional"
            }
            self.clear_old_real(aid)
            written.append(self.req("POST","/rest/v1/p55a_valuation_events",payload)[0])

        return {"status":"P5.6B6_REAL_VALUATION_BINDER_DONE","animals_scored":len(written),"top":sorted(written,key=lambda x:x["amount"],reverse=True)[:10]}
