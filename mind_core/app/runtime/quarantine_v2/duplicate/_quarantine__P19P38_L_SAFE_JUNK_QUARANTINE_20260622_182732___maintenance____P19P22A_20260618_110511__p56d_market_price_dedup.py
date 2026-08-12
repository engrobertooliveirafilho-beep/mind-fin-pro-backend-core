import requests, os, json, collections, datetime

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"return=representation"}

rows=requests.get(
    f"{u}/rest/v1/p55a_valuation_events?select=id,animal_id,amount,source_id,raw_payload,created_at&event_type=eq.P5.6D_MARKET_PRICE&order=created_at.asc&limit=5000",
    headers=h
).json()

groups=collections.defaultdict(list)

for r in rows:
    key=(
        r.get("animal_id"),
        str(r.get("amount")),
        r.get("source_id"),
        (r.get("raw_payload") or {}).get("classified_market_event")
    )
    groups[key].append(r)

deleted=[]

for key,items in groups.items():
    for x in items[1:]:
        resp=requests.delete(f"{u}/rest/v1/p55a_valuation_events?id=eq.{x['id']}",headers=h)
        if resp.status_code < 300:
            deleted.append(x["id"])

after=requests.get(
    f"{u}/rest/v1/p55a_valuation_events?select=id&event_type=eq.P5.6D_MARKET_PRICE&limit=5000",
    headers=h
).json()

audit={
    "mission":"P5.6D_MARKET_PRICE_DEDUP",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "before":len(rows),
    "groups":len(groups),
    "deleted":len(deleted),
    "after":len(after)
}

open("p56d_market_price_dedup_audit.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))
