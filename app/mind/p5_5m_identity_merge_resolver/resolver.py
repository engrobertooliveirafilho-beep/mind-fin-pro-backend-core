import os, json, urllib.request, urllib.parse, re

CHILD_TABLES = [
    ("p55a_media", "animal_id"),
    ("p55a_biomechanics", "animal_id"),
    ("p55a_judge_scores", "animal_id"),
    ("p55a_valuation_events", "animal_id"),
    ("p55a_reproduction_records", "animal_id")
]

EDGE_TABLES = [
    ("p55a_pedigree_edges", "parent_id"),
    ("p55a_pedigree_edges", "child_id")
]

def canon_name(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())

def canonical_choice(rows):
    return sorted(
        rows,
        key=lambda r: (
            -float(r.get("confidence_score") or 0),
            0 if r.get("country") else 1,
            0 if r.get("birth_year") else 1,
            0 if r.get("registry_number") else 1,
            r.get("created_at") or ""
        )
    )[0]

class IdentityMergeResolver:
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
            headers={
                "apikey":self.key,
                "Authorization":f"Bearer {self.key}",
                "Content-Type":"application/json",
                "Prefer":"return=representation"
            },
            method=method
        )
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def animals(self):
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name,aliases,registry_number,country,birth_year,confidence_score,created_at,notes")

    def duplicate_groups(self):
        groups={}
        for a in self.animals():
            groups.setdefault(canon_name(a.get("official_name")), []).append(a)
        return {k:v for k,v in groups.items() if k and len(v)>1}

    def patch_rows(self, table, field, old_id, new_id):
        q=urllib.parse.quote(old_id)
        return self.req("PATCH",f"/rest/v1/{table}?{field}=eq.{q}",{field:new_id})

    def delete_animal(self, animal_id):
        q=urllib.parse.quote(animal_id)
        return self.req("DELETE",f"/rest/v1/p55a_animals?id=eq.{q}")

    def merge_group(self, rows):
        canonical=canonical_choice(rows)
        old=[r for r in rows if r["id"] != canonical["id"]]
        actions=[]
        for dup in old:
            for table, field in CHILD_TABLES:
                try:
                    actions.append({"table":table,"field":field,"old":dup["id"],"new":canonical["id"],"rows":len(self.patch_rows(table,field,dup["id"],canonical["id"]))})
                except Exception as e:
                    actions.append({"table":table,"field":field,"error":str(e)})
            for table, field in EDGE_TABLES:
                try:
                    actions.append({"table":table,"field":field,"old":dup["id"],"new":canonical["id"],"rows":len(self.patch_rows(table,field,dup["id"],canonical["id"]))})
                except Exception as e:
                    actions.append({"table":table,"field":field,"error":str(e)})
            try:
                self.delete_animal(dup["id"])
                actions.append({"delete_duplicate":dup["id"],"status":"deleted"})
            except Exception as e:
                actions.append({"delete_duplicate":dup["id"],"error":str(e)})
        return {"canonical_id":canonical["id"],"canonical_name":canonical["official_name"],"merged_count":len(old),"actions":actions}

    def run(self):
        groups=self.duplicate_groups()
        results={name:self.merge_group(rows) for name,rows in groups.items()}
        return {"status":"P5.5M_IDENTITY_MERGE_DONE","groups":len(groups),"results":results}
