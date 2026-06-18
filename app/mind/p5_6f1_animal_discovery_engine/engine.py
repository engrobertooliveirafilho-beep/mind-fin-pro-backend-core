import os, json, re, hashlib, urllib.request
from collections import defaultdict

STOP = {"The","And","For","With","From","This","That","PBR","ABBI","PRCA","World","Champion","Bull","Bulls","Bucking","Classic","Futurity","Finals","Event","News","Video","Official"}
PATTERNS = [
    r"(?i)(?:bull|bucking bull|sire|dam|cow|offspring|son of|daughter of)\s+([A-Z][A-Za-z0-9' -]{2,40})",
    r"(?i)([A-Z][A-Za-z0-9' -]{2,40})\s+(?:bull|bucking bull|sire|dam|cow|offspring)",
    r"(?i)(?:by|out of)\s+([A-Z][A-Za-z0-9' -]{2,40})"
]

def clean_name(x):
    x=re.sub(r"[^A-Za-z0-9' -]"," ",str(x or "")).strip()
    x=re.sub(r"\s+"," ",x)
    parts=[p for p in x.split() if p not in STOP and p.lower() not in {s.lower() for s in STOP} and p.lower() not in {s.lower() for s in STOP}]
    return " ".join(parts).strip()[:80]

BAD_CANDIDATE_TERMS = ["price","sale","auction","score","history","biography","offspring","pedigree","sire","dam","semen","http","https","rodeo","rider","riders","professional","american","year","old","youtube","top","riding","greatest","point","genetics","sell","three-time","production","inc","red","baddest","legendary","yeti","provided","won","first ever","record-breaking","dangerous","joe berger","1996","list","com","site","www","official","profile","connection","catalog","registration","number","stats","news","article","videos","watch","search","two-time","most unridden","breeding program","embryo transfer","owner breeder","breeding fee","clone","dna","as a","great","nfr","calves","descendants","progeny"]

def is_valid_candidate_name(name):
    n=str(name or "").strip().lower()
    if len(n) < 3 or len(n) > 45: return False
    if any(x in n for x in BAD_CANDIDATE_TERMS): return False
    if re.search(r"\b(of|and|the|was|in|for|with|from|to|by|as|a|most|great|fee|owner|breeder|program|embryo|transfer|clone|dna|nfr)\b", n): return False
    if len(n.split()) > 4: return False
    if n in {"list","com","site","www","bull","bucking","official","profile"}: return False
    if "." in n or "/" in n or "_" in n: return False
    return True

def candidate_hash(name):
    return hashlib.sha256(name.lower().encode()).hexdigest()

class AnimalDiscoveryEngine:
    def __init__(self,url=None,key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self,method,path,payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def sources(self,limit=1000):
        return self.req("GET",f"/rest/v1/p55a_sources?select=id,source_url,title,raw_payload,confidence_score&order=created_at.desc&limit={limit}")

    def animals(self):
        rows=self.req("GET","/rest/v1/p55a_animals?select=id,official_name&limit=10000")
        return {str(r.get("official_name") or "").lower():r for r in rows}

    def extract_candidates(self, source):
        blob=" ".join([str(source.get("title") or ""),str(source.get("source_url") or ""),json.dumps(source.get("raw_payload") or {},ensure_ascii=False)])
        found=[]
        for p in PATTERNS:
            for m in re.findall(p, blob):
                name=clean_name(m)
                if is_valid_candidate_name(name): found.append(name)
        return list(dict.fromkeys(found))

    def promote_animal(self,name,sources):
        existing=self.animals()
        if name.lower() in existing:
            return {"status":"already_exists","name":name,"animal_id":existing[name.lower()]["id"]}
        payload={
            "official_name":name,
            "country":"Unknown",
            "life_status":"unknown",
            "confidence_score":min(95,20+len(sources)*15),
            "notes":"P5.6F1 autonomous discovery"}
        row=self.req("POST","/rest/v1/p55a_animals",payload)[0]
        return {"status":"promoted","name":name,"animal_id":row["id"]}

    def run_once(self,limit=1000,min_sources=3):
        srcs=self.sources(limit)
        grouped=defaultdict(list)
        for s in srcs:
            for name in self.extract_candidates(s):
                grouped[name].append({"source_id":s["id"],"title":s.get("title"),"url":s.get("source_url")})

        promoted=[]; candidates=[]
        for name,evs in grouped.items():
            conf=min(100,20+len(evs)*15)
            item={"name":name,"sources":len(evs),"confidence":conf}
            candidates.append(item)
            if False: promoted.append(self.promote_animal(name,evs))

        return {
            "status":"P5.6F1_ANIMAL_DISCOVERY_ENGINE_DONE",
            "sources_scanned":len(srcs),
            "candidates_found":len(candidates),
            "promoted":sum(1 for x in promoted if x["status"]=="promoted"),
            "already_exists":sum(1 for x in promoted if x["status"]=="already_exists"),
            "top_candidates":sorted(candidates,key=lambda x:x["confidence"],reverse=True)[:20],
            "promotions":promoted[:20],
            "next_action":"RERUN_P5.6F_AUTONOMOUS_LOOP"
        }









