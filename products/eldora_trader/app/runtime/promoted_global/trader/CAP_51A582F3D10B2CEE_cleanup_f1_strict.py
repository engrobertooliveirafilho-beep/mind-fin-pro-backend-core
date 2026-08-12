import os,json,re,urllib.request
url=os.getenv("SUPABASE_URL","").rstrip("/")
key=os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

BAD_PATTERNS=[
 "price","sale","auction","score","rodeo","history","biography","offspring",
 "pedigree","sire","dam","semen","http","https","yearling","professional",
 "american","greatest","rider","bull riders","buck-offs","old"
]

KEEP={"bushwacker","woopaa","bodacious","little yellow jacket","bruiser","asteroid","whitewater skoal","lady luck","j31 bodacious cow","miss marie laveau","red wolf"}

def req(m,p,payload=None):
    data=json.dumps(payload).encode() if payload is not None else None
    r=urllib.request.Request(url+p,data=data,headers={"apikey":key,"Authorization":"Bearer "+key,"Content-Type":"application/json","Prefer":"return=representation"},method=m)
    with urllib.request.urlopen(r,timeout=30) as x:
        body=x.read().decode()
        return json.loads(body) if body else []

def bad_name(name):
    n=(name or "").strip().lower()
    if n in KEEP: return False
    if len(n)<3 or len(n)>45: return True
    if any(p in n for p in BAD_PATTERNS): return True
    if re.search(r"\b(of|and|the|was|in|for|with|from)\b", n): return True
    if len(n.split())>4: return True
    return False

rows=req("GET","/rest/v1/p55a_animals?select=id,official_name,confidence_score&limit=10000")
deleted=[]
seen={}
merged=[]

for r in rows:
    name=(r.get("official_name") or "").strip()
    nl=name.lower()
    if bad_name(name):
        req("DELETE","/rest/v1/p55a_animals?id=eq."+r["id"])
        deleted.append(name)
        continue
    if nl in seen:
        keep=seen[nl]
        old=r["id"]; new=keep["id"]
        for table,field in [
            ("p55a_media","animal_id"),
            ("p55a_biomechanics","animal_id"),
            ("p55a_judge_scores","animal_id"),
            ("p55a_valuation_events","animal_id"),
            ("p55a_reproduction_records","animal_id"),
            ("p55a_pedigree_edges","parent_id"),
            ("p55a_pedigree_edges","child_id")
        ]:
            try:
                req("PATCH",f"/rest/v1/{table}?{field}=eq.{old}",{field:new})
            except Exception:
                pass
        req("DELETE","/rest/v1/p55a_animals?id=eq."+old)
        merged.append({"name":name,"from":old,"to":new})
    else:
        seen[nl]=r

print({"status":"P5.6F1_STRICT_CLEANUP_DONE","deleted_count":len(deleted),"merged_count":len(merged),"deleted":deleted[:80],"merged":merged})
