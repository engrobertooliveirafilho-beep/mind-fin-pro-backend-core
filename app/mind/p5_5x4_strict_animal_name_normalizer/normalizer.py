import os, json, urllib.request, urllib.parse, re

DELETE_PATTERNS = [
    r"\bpartnership\b",
    r"\bappointment\b",
    r"\bweekends?\b",
    r"\bonly\b",
    r"\bcontact\b",
    r"\bprices?\b",
    r"\bconsigned\b",
    r"\bbulls in\b"
]

REL_SUFFIX = re.compile(r"\s+\b(SIRE|DAM)\b\s*$", re.I)

def should_delete(name):
    n=re.sub(r"\s+"," ",str(name or "").strip().lower())
    return any(re.search(p,n) for p in DELETE_PATTERNS) or len(n.split()) > 5

def normalized_name(name):
    n=re.sub(r"\s+"," ",str(name or "").strip())
    n=REL_SUFFIX.sub("", n).strip()
    return n

class StrictAnimalNameNormalizer:
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

    def patch_animal_name(self, animal_id, name):
        q=urllib.parse.quote(animal_id)
        return self.req("PATCH",f"/rest/v1/p55a_animals?id=eq.{q}",{"official_name":name,"notes":"P5.5X4 normalized probable animal name; source validation still required."})

    def run(self):
        deleted=[]; normalized=[]; edges_deleted=0; animals_deleted=0
        for a in self.animals():
            name=a.get("official_name") or ""
            if should_delete(name):
                edges_deleted += len(self.delete_where("p55a_pedigree_edges","parent_id",a["id"]))
                edges_deleted += len(self.delete_where("p55a_pedigree_edges","child_id",a["id"]))
                for table in ["p55a_media","p55a_biomechanics","p55a_judge_scores","p55a_valuation_events","p55a_reproduction_records"]:
                    try: self.delete_where(table,"animal_id",a["id"])
                    except Exception: pass
                animals_deleted += len(self.delete_where("p55a_animals","id",a["id"]))
                deleted.append(name)
                continue

            nn=normalized_name(name)
            if nn != name and len(nn) >= 3:
                self.patch_animal_name(a["id"], nn)
                normalized.append({"old":name,"new":nn})

        return {"status":"P5.5X4_STRICT_ANIMAL_NAME_NORMALIZER_DONE","deleted":len(deleted),"normalized":len(normalized),"edges_deleted":edges_deleted,"animals_deleted":animals_deleted,"deleted_names":deleted,"normalized_names":normalized,"next_action":"RECALCULATE_P5.5X_GRAPH"}
