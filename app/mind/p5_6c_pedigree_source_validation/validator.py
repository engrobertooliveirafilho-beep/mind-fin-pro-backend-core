import os, json, urllib.request, urllib.parse, re

STRONG_TERMS=["sire","dam","father","mother","son of","daughter of","out of","by "]
WEAK_TERMS=["family","legend","history","documentary","mentioned","related"]

def evidence_score(payload):
    txt=json.dumps(payload or {},ensure_ascii=False).lower()
    score=20
    score += 35 if any(t in txt for t in STRONG_TERMS) else 0
    score -= 20 if any(t in txt for t in WEAK_TERMS) else 0
    score += 15 if "registry" in txt or "abbi" in txt or "pbr" in txt else 0
    return max(0,min(100,score))

def status_from_score(score):
    if score >= 70: return "validated"
    if score >= 45: return "needs_review"
    return "blocked_low_evidence"

class PedigreeSourceValidator:
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

    def edges(self):
        return self.req("GET","/rest/v1/p55a_pedigree_edges?select=*&limit=10000")

    def sources(self):
        return self.req("GET","/rest/v1/p55a_sources?select=id,source_url,title,raw_payload,confidence_score&limit=10000")

    def run_once(self):
        edges=self.edges()
        sources=self.sources()
        validations=[]
        for e in edges:
            best=None
            for s in sources:
                sc=evidence_score(s)
                if best is None or sc > best["score"]:
                    best={"source_id":s["id"],"source_url":s.get("source_url"),"score":sc,"title":s.get("title")}
            status=status_from_score(best["score"] if best else 0)
            payload={
                "entity_type":"pedigree_edge",
                "entity_id":e.get("id"),
                "audit_type":"P5.6C_PEDIGREE_SOURCE_VALIDATION",
                "confidence_score":best["score"] if best else 0,
                "evidence_count":1 if best else 0,
                "source_count":1 if best else 0,
                "conflict_count":0,
                "missing_fields":[] if status=="validated" else ["strong_source_evidence"],
                "contradictions":[],
                "audit_status":status,
                "raw_payload":{"edge":e,"best_source":best,"validation_status":status}
            }
            try:
                validations.append(self.req("POST","/rest/v1/p55a_audit_logs",payload)[0])
            except Exception:
                payload.pop("raw_payload",None)
                validations.append(self.req("POST","/rest/v1/p55a_audit_logs",payload)[0])
        return {
            "status":"P5.6C_PEDIGREE_SOURCE_VALIDATION_DONE",
            "edges_scanned":len(edges),
            "audits_created":len(validations),
            "validated":sum(1 for v in validations if v.get("audit_status")=="validated"),
            "needs_review":sum(1 for v in validations if v.get("audit_status")=="needs_review"),
            "blocked":sum(1 for v in validations if v.get("audit_status")=="blocked_low_evidence"),
            "next_action":"P5.6D_MARKET_VALUATION_REAL_PRICES"
        }
