import os,json,re,urllib.request

KEEP={"bushwacker","woopaa","bodacious","little yellow jacket","bruiser","asteroid","whitewater skoal","lady luck","j31 bodacious cow","miss marie laveau","red wolf"}
BAD=["youtube","price","sale","auction","score","history","biography","offspring","pedigree","sire","dam","semen","http","https","rodeo","rider","professional","american","year","old","provided","won","first ever","record","dangerous","championship","award","title","great","tallied"]

def is_bad(name):
    n=(name or "").strip().lower()
    if n in KEEP: return False
    if len(n)<3 or len(n)>45: return True
    if any(x in n for x in BAD): return True
    if re.search(r"\b(of|and|the|was|in|for|with|from|to|by|his|he|are|more|than)\b", n): return True
    if len(n.split())>4: return True
    return False

class DatabaseSanitizer:
    def __init__(self,url=None,key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self,m,p,payload=None):
        data=json.dumps(payload).encode() if payload is not None else None
        r=urllib.request.Request(self.url+p,data=data,headers={"apikey":self.key,"Authorization":"Bearer "+self.key,"Content-Type":"application/json","Prefer":"return=representation"},method=m)
        with urllib.request.urlopen(r,timeout=30) as x:
            b=x.read().decode()
            return json.loads(b) if b else []

    def delete_dependents(self,animal_id):
        report={}
        for table,field in [
            ("p55a_media","animal_id"),
            ("p55a_biomechanics","animal_id"),
            ("p55a_judge_scores","animal_id"),
            ("p55a_valuation_events","animal_id"),
            ("p55a_reproduction_records","animal_id")
        ]:
            try:
                old=self.req("GET",f"/rest/v1/{table}?{field}=eq.{animal_id}&select=id&limit=10000")
                for r in old: self.req("DELETE",f"/rest/v1/{table}?id=eq.{r['id']}")
                report[table]=len(old)
            except Exception:
                report[table]="skip"
        for field in ["parent_id","child_id"]:
            try:
                old=self.req("GET",f"/rest/v1/p55a_pedigree_edges?{field}=eq.{animal_id}&select=id&limit=10000")
                for r in old: self.req("DELETE",f"/rest/v1/p55a_pedigree_edges?id=eq.{r['id']}")
                report["p55a_pedigree_edges_"+field]=len(old)
            except Exception:
                report["p55a_pedigree_edges_"+field]="skip"
        return report

    def run_once(self):
        animals=self.req("GET","/rest/v1/p55a_animals?select=id,official_name&limit=10000")
        deleted=[]
        for a in animals:
            name=a.get("official_name") or ""
            if is_bad(name):
                deps=self.delete_dependents(a["id"])
                self.req("DELETE","/rest/v1/p55a_animals?id=eq."+a["id"])
                deleted.append({"id":a["id"],"name":name,"deps":deps})
        return {"status":"P5.6F2_DATABASE_SANITIZER_DONE","animals_scanned":len(animals),"deleted_count":len(deleted),"deleted":deleted[:100]}
