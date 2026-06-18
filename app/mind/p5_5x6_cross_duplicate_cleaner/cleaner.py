import os, json, urllib.request, urllib.parse, re

def canon_name(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())

def is_cross_fragment(name):
    n=str(name or "")
    return bool(re.search(r"\s+[xX]\s+", n)) or "." in n

class CrossDuplicateCleaner:
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
        return self.req("GET","/rest/v1/p55a_animals?select=id,official_name,country,birth_year,registry_number,confidence_score,created_at")

    def delete_where(self, table, field, value):
        q=urllib.parse.quote(value)
        return self.req("DELETE",f"/rest/v1/{table}?{field}=eq.{q}")

    def patch_where(self, table, field, old_id, new_id):
        q=urllib.parse.quote(old_id)
        return self.req("PATCH",f"/rest/v1/{table}?{field}=eq.{q}",{field:new_id})

    def delete_animal_full(self, animal_id):
        deleted_edges=0
        deleted_edges += len(self.delete_where("p55a_pedigree_edges","parent_id",animal_id))
        deleted_edges += len(self.delete_where("p55a_pedigree_edges","child_id",animal_id))
        for table in ["p55a_media","p55a_biomechanics","p55a_judge_scores","p55a_valuation_events","p55a_reproduction_records"]:
            try: self.delete_where(table,"animal_id",animal_id)
            except Exception: pass
        deleted_animals=len(self.delete_where("p55a_animals","id",animal_id))
        return deleted_edges, deleted_animals

    def canonical_choice(self, rows):
        return sorted(rows, key=lambda r: (
            -float(r.get("confidence_score") or 0),
            0 if r.get("country") else 1,
            0 if r.get("birth_year") else 1,
            0 if r.get("registry_number") else 1,
            r.get("created_at") or ""
        ))[0]

    def merge_duplicates(self):
        groups={}
        for a in self.animals():
            groups.setdefault(canon_name(a["official_name"]), []).append(a)

        merged=[]
        for name, rows in groups.items():
            if len(rows) < 2:
                continue
            can=self.canonical_choice(rows)
            for dup in rows:
                if dup["id"] == can["id"]:
                    continue
                for table in ["p55a_media","p55a_biomechanics","p55a_judge_scores","p55a_valuation_events","p55a_reproduction_records"]:
                    try: self.patch_where(table,"animal_id",dup["id"],can["id"])
                    except Exception: pass
                for field in ["parent_id","child_id"]:
                    try: self.patch_where("p55a_pedigree_edges",field,dup["id"],can["id"])
                    except Exception: pass
                try: self.delete_where("p55a_animals","id",dup["id"])
                except Exception: pass
                merged.append({"name":name,"from":dup["id"],"to":can["id"]})
        return merged

    def run(self):
        deleted=[]; edges_deleted=0; animals_deleted=0
        for a in self.animals():
            if is_cross_fragment(a["official_name"]):
                e,d=self.delete_animal_full(a["id"])
                edges_deleted += e
                animals_deleted += d
                deleted.append(a["official_name"])
        merged=self.merge_duplicates()
        return {
            "status":"P5.5X6_CROSS_DUPLICATE_CLEANER_DONE",
            "cross_fragments_deleted":len(deleted),
            "animals_deleted":animals_deleted,
            "edges_deleted":edges_deleted,
            "deleted_names":deleted,
            "duplicates_merged":len(merged),
            "merged":merged,
            "next_action":"RECALCULATE_P5.5X_GRAPH"
        }
