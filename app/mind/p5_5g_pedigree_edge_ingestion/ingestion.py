import os, json, urllib.request, urllib.parse, hashlib, re

def norm(x): return re.sub(r"\s+"," ",str(x or "").strip().lower())

def animal_key(name, registry_number=None, birth_year=None):
    seed="|".join([norm(name), str(registry_number or ""), str(birth_year or "")])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()

PEDIGREE_SEEDS = [
 {"parent_name":"Whitewater Skoal","child_name":"Bushwacker","relation":"sire","confidence_score":60,"validation_status":"provisional"},
 {"parent_name":"Lady Luck","child_name":"Bushwacker","relation":"dam","confidence_score":60,"validation_status":"provisional"},
 {"parent_name":"A6","child_name":"Bodacious","relation":"sire","confidence_score":60,"validation_status":"provisional"},
 {"parent_name":"J31 Bodacious Cow","child_name":"Bodacious","relation":"dam","confidence_score":40,"validation_status":"weak"}
]

class PedigreeEdgeIngestion:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key: raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x: return json.loads(x.read().decode("utf-8"))

    def upsert_animal_min(self, name):
        p={"official_name":name,"animal_type":"bull","life_status":"unknown","identity_key":animal_key(name),"confidence_score":40,"validation_status":"weak","notes":"Auto-created by P5.5G pedigree seed; requires validation."}
        return self.req("POST","/rest/v1/p55a_animals?on_conflict=identity_key",p)[0]

    def find_or_create(self, name):
        key=animal_key(name)
        q=urllib.parse.quote(key)
        rows=self.req("GET",f"/rest/v1/p55a_animals?identity_key=eq.{q}&select=id,official_name,identity_key")
        return rows[0] if rows else self.upsert_animal_min(name)

    def upsert_edge(self, parent_name, child_name, relation, confidence_score=40, validation_status="weak"):
        parent=self.find_or_create(parent_name); child=self.find_or_create(child_name)
        payload={"parent_id":parent["id"],"child_id":child["id"],"relation":relation,"generation_distance":1,"confidence_score":confidence_score,"validation_status":validation_status}
        return self.req("POST","/rest/v1/p55a_pedigree_edges?on_conflict=parent_id,child_id,relation",payload)[0]

    def seed(self):
        return [self.upsert_edge(**x) for x in PEDIGREE_SEEDS]

    def audit(self, rows):
        return {"status":"P5.5G_PEDIGREE_EDGES_SEEDED","total":len(rows),"unique_edges":len(set((r["parent_id"],r["child_id"],r["relation"]) for r in rows)),"ids":[r["id"] for r in rows]}
