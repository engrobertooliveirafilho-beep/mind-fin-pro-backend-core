import os, json, urllib.request, urllib.parse, re

BLACKLIST = [
    "dam offspring","offspring","competition stats http","competition stats",
    "pedigree","sire","dam","semen","auction","score","video","http","https",
    "the joe berger family of mandan"
]

def bad_name(name):
    n = re.sub(r"\s+", " ", str(name or "").strip().lower())
    if n in BLACKLIST:
        return True
    if len(n) < 3:
        return True
    if n.startswith("http") or "http" in n:
        return True
    if n in ["sire", "dam", "offspring", "pedigree"]:
        return True
    return False

class FakeAnimalCleaner:
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
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name")

    def delete_where(self, table, field, value):
        q=urllib.parse.quote(value)
        return self.req("DELETE",f"/rest/v1/{table}?{field}=eq.{q}")

    def run(self):
        bad=[a for a in self.animals() if bad_name(a.get("official_name"))]
        deleted_edges=0
        deleted_animals=0

        for a in bad:
            deleted_edges += len(self.delete_where("p55a_pedigree_edges","parent_id",a["id"]))
            deleted_edges += len(self.delete_where("p55a_pedigree_edges","child_id",a["id"]))
            for table in ["p55a_media","p55a_biomechanics","p55a_judge_scores","p55a_valuation_events","p55a_reproduction_records"]:
                try:
                    self.delete_where(table,"animal_id",a["id"])
                except Exception:
                    pass
            deleted_animals += len(self.delete_where("p55a_animals","id",a["id"]))

        return {
            "status":"P5.5X1_FAKE_ANIMAL_CLEANER_DONE",
            "bad_detected":len(bad),
            "animals_deleted":deleted_animals,
            "edges_deleted":deleted_edges,
            "deleted_names":[a["official_name"] for a in bad],
            "next_action":"RECALCULATE_P5.5X_GRAPH"
        }
