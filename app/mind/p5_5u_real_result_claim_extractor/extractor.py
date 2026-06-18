import os, json, re, urllib.request

CLAIM_PATTERNS = {
    "registry_numbers": r"\b\d{1,3}[/.-]\d{1,3}\b",
    "years": r"\b(19[7-9]\d|20[0-3]\d)\b",
    "scores": r"\b([4-9]\d(?:\.\d+)?)\b",
    "money_values": r"[$R]\$?\s?\d[\d.,]*",
}

KEYWORDS = ["pedigree","sire","dam","offspring","semen","auction","sale","pbr","abbi","prca","nfr","score","bull ride","bucking bull"]

def extract_claims(text):
    t=str(text or "")
    low=t.lower()
    return {
        "patterns": {k: re.findall(v,t) for k,v in CLAIM_PATTERNS.items()},
        "keywords": [k for k in KEYWORDS if k in low],
        "has_pedigree_signal": any(k in low for k in ["pedigree","sire","dam","offspring"]),
        "has_market_signal": any(k in low for k in ["semen","auction","sale","price"]),
        "has_video_signal": any(k in low for k in ["youtube","video","bull ride"]),
        "claim_strength": min(100, len([k for k in KEYWORDS if k in low])*8 + sum(len(re.findall(v,t)) for v in CLAIM_PATTERNS.values())*5)
    }

class RealResultClaimExtractor:
    def __init__(self, url=None, key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key: raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def real_sources(self, limit=250):
        return self.req("GET",f"/rest/v1/p55a_sources?source_type=eq.REAL_SEARCH_RESULT&select=id,source_url,title,raw_payload,confidence_score,validation_status&order=created_at.desc&limit={limit}")

    def audit_source(self, source):
        raw=source.get("raw_payload") or {}
        text=" ".join([str(source.get("title") or ""), str(source.get("source_url") or ""), str(raw.get("snippet") or ""), json.dumps(raw, ensure_ascii=False)])
        claims=extract_claims(text)
        payload={
            "entity_type":"source",
            "entity_id":source["id"],
            "audit_type":"P5.5U_REAL_RESULT_CLAIM_EXTRACTION",
            "confidence_score":claims["claim_strength"],
            "evidence_count":1,
            "source_count":1,
            "conflict_count":0,
            "missing_fields":[] if claims["claim_strength"] >= 40 else ["weak_claim_signal"],
            "contradictions":[],
            "audit_status":"provisional" if claims["claim_strength"] >= 40 else "weak"
        }
        row=self.req("POST","/rest/v1/p55a_audit_logs",payload)[0]
        return {"source_id":source["id"],"audit_id":row["id"],"claims":claims}

    def run_once(self, limit=250):
        sources=self.real_sources(limit)
        results=[self.audit_source(s) for s in sources]
        strong=sum(1 for r in results if r["claims"]["claim_strength"]>=40)
        return {"status":"P5.5U_REAL_RESULT_CLAIM_EXTRACTOR_DONE","sources_processed":len(sources),"audits_created":len(results),"strong_claims":strong,"next_action":"P5.5V_PEDIGREE_EXTRACTOR"}
