import os, json, urllib.request, urllib.parse, re

def extract_claims(text):
    text = str(text or "")
    return {
        "possible_registry_numbers": re.findall(r"\b\d{1,3}[/.-]\d{1,3}\b", text),
        "possible_years": re.findall(r"\b(19[7-9]\d|20[0-3]\d)\b", text),
        "possible_scores": re.findall(r"\b([4-9]\d(?:\.\d+)?)\b", text),
        "possible_platforms": [x for x in ["PBR","ABBI","PRCA","NFR","YouTube","auction","semen","pedigree"] if x.lower() in text.lower()]
    }

class WorkerFetchParse:
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

    def pending_sources(self, limit=50):
        return self.req("GET",f"/rest/v1/p55a_sources?select=id,source_url,source_type,title,raw_payload,confidence_score,validation_status&order=created_at.desc&limit={limit}")

    def audit_source(self, source):
        text=" ".join([str(source.get("title") or ""), str(source.get("source_url") or ""), json.dumps(source.get("raw_payload") or {}, ensure_ascii=False)])
        claims=extract_claims(text)
        gaps=[]
        if not claims["possible_platforms"]: gaps.append("platform_context_weak")
        if not claims["possible_years"]: gaps.append("year_missing")
        payload={
            "entity_type":"source",
            "entity_id":source["id"],
            "audit_type":"P5.5Q_FETCH_PARSE_METADATA",
            "confidence_score":source.get("confidence_score") or 0,
            "evidence_count":1,
            "source_count":1,
            "conflict_count":0,
            "missing_fields":gaps,
            "contradictions":[],
            "audit_status":source.get("validation_status") or "provisional"
        }
        row=self.req("POST","/rest/v1/p55a_audit_logs",payload)[0]
        return {"source_id":source["id"],"claims":claims,"audit_id":row["id"]}

    def run_once(self, limit=50):
        sources=self.pending_sources(limit)
        results=[self.audit_source(s) for s in sources]
        return {
            "status":"P5.5Q_WORKER_FETCH_PARSE_DONE",
            "sources_processed":len(sources),
            "audits_created":len(results),
            "next_action":"P5.5R_CLAIM_TO_ENTITY_PROMOTER"
        }
