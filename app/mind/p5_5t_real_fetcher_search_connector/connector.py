import os, json, urllib.request, urllib.parse, hashlib

def h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()

class RealFetcherSearchConnector:
    def __init__(self, url=None, key=None, search_key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        self.search_key=search_key or os.getenv("SERPAPI_KEY") or os.getenv("SEARCH_API_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self, method, path, payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def query_sources(self, limit=25):
        return self.req("GET",f"/rest/v1/p55a_sources?source_type=in.(SEARCH_QUERY,PEDIGREE_SEARCH,SEMEN_MARKET_SEARCH,AUCTION_SEARCH,VIDEO_SEARCH,OFFSPRING_SEARCH,HISTORY_SEARCH)&select=id,source_url,source_type,title,raw_payload,evidence_hash&order=created_at.desc&limit={limit}")

    def extract_query(self, source):
        raw=source.get("raw_payload") or {}
        if raw.get("query"): return raw["query"]
        url=source.get("source_url") or ""
        parsed=urllib.parse.urlparse(url)
        qs=urllib.parse.parse_qs(parsed.query)
        return (qs.get("q") or [""])[0]

    def search_serpapi(self, query):
        if not self.search_key:
            return []
        api="https://serpapi.com/search.json?engine=google&q="+urllib.parse.quote(query)+"&api_key="+urllib.parse.quote(self.search_key)
        with urllib.request.urlopen(api,timeout=30) as r:
            data=json.loads(r.read().decode("utf-8"))
        return data.get("organic_results", [])[:10]

    def result_to_source(self, parent, result, query):
        url=result.get("link") or result.get("url")
        title=result.get("title") or f"Search result: {query}"
        snippet=result.get("snippet") or ""
        payload={
            "source_url":url,
            "source_type":"REAL_SEARCH_RESULT",
            "title":title,
            "platform":"web",
            "raw_payload":{"mission":"P5.5T","query":query,"parent_source_id":parent["id"],"snippet":snippet},
            "confidence_score":60,
            "validation_status":"provisional"
        }
        payload["evidence_hash"]=h({"url":url,"title":title,"query":query})
        return payload

    def upsert_source(self, payload):
        return self.req("POST","/rest/v1/p55a_sources?on_conflict=evidence_hash",payload)[0]

    def audit(self, parent, query, mode, produced):
        payload={
            "entity_type":"source",
            "entity_id":parent["id"],
            "audit_type":"P5.5T_REAL_FETCHER_SEARCH_CONNECTOR",
            "confidence_score":60 if produced else 35,
            "evidence_count":produced,
            "source_count":1,
            "conflict_count":0,
            "missing_fields":[] if self.search_key else ["SERPAPI_KEY_OR_SEARCH_API_KEY"],
            "contradictions":[],
            "audit_status":"provisional"
        }
        return self.req("POST","/rest/v1/p55a_audit_logs",payload)

    def run_once(self, limit=10):
        parents=self.query_sources(limit)
        created=[]
        prepared=[]
        for p in parents:
            q=self.extract_query(p)
            results=self.search_serpapi(q)
            if not results:
                prepared.append({"parent_source_id":p["id"],"query":q,"mode":"prepared_no_search_key_or_no_results"})
                self.audit(p,q,"prepared",0)
                continue
            for r in results:
                src=self.result_to_source(p,r,q)
                if src.get("source_url"):
                    created.append(self.upsert_source(src))
            self.audit(p,q,"real_search",len(results))
        return {"status":"P5.5T_REAL_FETCHER_SEARCH_CONNECTOR_DONE","parents_scanned":len(parents),"real_sources_created":len(created),"prepared_only":len(prepared),"search_key_available":bool(self.search_key),"next_action":"P5.5U_REAL_RESULT_CLAIM_EXTRACTOR"}
