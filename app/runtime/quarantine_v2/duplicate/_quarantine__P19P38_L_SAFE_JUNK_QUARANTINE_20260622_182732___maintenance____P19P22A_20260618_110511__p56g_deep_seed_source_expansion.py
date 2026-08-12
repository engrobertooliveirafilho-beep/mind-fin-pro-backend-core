import os,json,hashlib,urllib.parse,datetime,requests

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"}

animals=requests.get(f"{u}/rest/v1/p55a_animals?select=id,official_name,notes&notes=ilike.*P5.6G manual audited seed*",headers=h).json()

templates=[
    "{name} PBR bull ride YouTube",
    "{name} official PBR bucking bull",
    "{name} ABBI pedigree sire dam",
    "{name} bucking bull offspring",
    "{name} bucking bull progeny",
    "{name} semen price bucking bull",
    "{name} auction sale price bucking bull",
    "{name} owner breeder stock contractor",
    "{name} PRCA NFR bucking bull",
    "{name} world champion bucking bull"
]

created=[]
for a in animals:
    for tpl in templates:
        q=tpl.format(name=a["official_name"])
        url="https://www.google.com/search?q="+urllib.parse.quote(q)
        eh=hashlib.sha256(json.dumps({"mission":"P5.6G_DEEP_SEED_EXPANSION","animal_id":a["id"],"query":q},sort_keys=True).encode()).hexdigest()
        payload={
            "source_url":url,
            "source_type":"P5.6G_SEED_DEEP_SEARCH_QUERY",
            "title":"P5.6G seed deep expansion: "+q,
            "platform":"search",
            "raw_payload":{"mission":"P5.6G_SEED_DEEP_EXPANSION","animal_id":a["id"],"animal_name":a["official_name"],"query":q},
            "confidence_score":60,
            "validation_status":"provisional",
            "evidence_hash":eh
        }
        r=requests.post(f"{u}/rest/v1/p55a_sources?on_conflict=evidence_hash",headers=h,json=payload)
        if r.status_code<300:
            created+=r.json()

count=requests.get(f"{u}/rest/v1/p55a_sources?select=id&limit=1",headers={**h,"Prefer":"count=exact"}).headers.get("content-range")
audit={"mission":"P5.6G_DEEP_SEED_SOURCE_EXPANSION","created_at":datetime.datetime.now(datetime.UTC).isoformat(),"seed_animals":len(animals),"queries_per_animal":len(templates),"created_or_upserted":len(created),"sources_count":count}
open("p56g_deep_seed_source_expansion.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))
