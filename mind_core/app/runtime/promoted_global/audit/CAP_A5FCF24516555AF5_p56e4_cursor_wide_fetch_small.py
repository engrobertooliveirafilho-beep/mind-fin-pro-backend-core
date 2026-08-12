import os, json, urllib.request, urllib.parse, hashlib, time, requests, datetime

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
sk=os.getenv("SERPAPI_KEY") or os.getenv("SEARCH_API_KEY")

h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"}

def hh(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()

def get(path):
    return requests.get(u+path,headers=h).json()

def post(path,payload):
    return requests.post(u+path,headers=h,json=payload)

parents=get("/rest/v1/p55a_sources?select=id,source_url,title,raw_payload,evidence_hash&source_type=eq.P5.6E4_WIDE_SEARCH_QUERY&order=created_at.asc&limit=40")
done=get("/rest/v1/p55a_sources?select=raw_payload&source_type=eq.REAL_SEARCH_RESULT&limit=5000")
done_ids=set()
for d in done:
    raw=d.get("raw_payload") or {}
    if raw.get("parent_source_id"):
        done_ids.add(raw["parent_source_id"])

created=[]
errors=[]
processed=0

for p in parents:
    if p["id"] in done_ids:
        continue
    raw=p.get("raw_payload") or {}
    q=raw.get("query") or urllib.parse.parse_qs(urllib.parse.urlparse(p.get("source_url","")).query).get("q",[""])[0]
    if not q:
        continue
    api="https://serpapi.com/search.json?engine=google&q="+urllib.parse.quote(q)+"&api_key="+urllib.parse.quote(sk)
    try:
        data=json.loads(urllib.request.urlopen(api,timeout=35).read().decode())
        results=data.get("organic_results",[])[:10]
        for r in results:
            url=r.get("link") or r.get("url")
            if not url: continue
            title=r.get("title") or q
            payload={
                "source_url":url,
                "source_type":"REAL_SEARCH_RESULT",
                "title":title,
                "platform":"web",
                "raw_payload":{"mission":"P5.6E4_CURSOR_FETCH","query":q,"parent_source_id":p["id"],"snippet":r.get("snippet")},
                "confidence_score":65,
                "validation_status":"provisional",
                "evidence_hash":hh({"url":url,"query":q,"parent":p["id"]})
            }
            resp=post("/rest/v1/p55a_sources?on_conflict=evidence_hash",payload)
            if resp.status_code<300:
                created+=resp.json()
            else:
                errors.append({"query":q,"status":resp.status_code,"text":resp.text})
        processed+=1
        time.sleep(2)
    except Exception as e:
        errors.append({"query":q,"error":str(e)})

count=requests.get(u+"/rest/v1/p55a_sources?select=id&limit=1",headers={**h,"Prefer":"count=exact"}).headers.get("content-range")
audit={"mission":"P5.6E4_CURSOR_DEEP_FETCH","created_at":datetime.datetime.now(datetime.UTC).isoformat(),"parents_loaded":len(parents),"processed_new_parents":processed,"created_or_upserted":len(created),"errors":len(errors),"sources_count":count}
open("p56e4_cursor_deep_fetch_audit.json","w",encoding="utf-8").write(json.dumps({"audit":audit,"errors":errors[:20]},ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))


