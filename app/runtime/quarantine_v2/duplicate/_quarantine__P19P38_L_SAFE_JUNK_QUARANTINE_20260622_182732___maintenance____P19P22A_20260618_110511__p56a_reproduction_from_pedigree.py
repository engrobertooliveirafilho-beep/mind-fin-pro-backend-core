import requests, os, json, datetime

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"return=representation"}

edges=requests.get(f"{u}/rest/v1/p55a_pedigree_edges?select=parent_id,child_id,relation,confidence_score,validation_status",headers=h).json()
before=requests.get(f"{u}/rest/v1/p55a_reproduction_records?select=id",headers=h).json()

created=[]
skipped=[]

for e in edges:
    rel=(e.get("relation") or "").lower()
    payload={
        "animal_id":e["parent_id"],
        "offspring_id":e["child_id"],
        "confidence_score":e.get("confidence_score") or 60,
        "validation_status":e.get("validation_status") or "provisional",
        "semen_available":None,
        "embryo_available":None,
        "pregnancy_available":None,
        "dna_available":None,
        "genomic_payload":{"source":"p55a_pedigree_edges","relation":rel},
        "reproductive_payload":{"mission":"P5.6A_REPRODUCTION_FROM_PEDIGREE_EDGES","created_from_edge":e}
    }

    if "sire" in rel or "father" in rel or rel=="parent":
        payload["sire_id"]=e["parent_id"]
    elif "dam" in rel or "mother" in rel:
        payload["dam_id"]=e["parent_id"]
    else:
        payload["genomic_payload"]["relation_unclassified"]=rel

    dup_url=f"{u}/rest/v1/p55a_reproduction_records?select=id&animal_id=eq.{payload['animal_id']}&offspring_id=eq.{payload['offspring_id']}"
    dup=requests.get(dup_url,headers=h).json()

    if dup:
        skipped.append({"reason":"duplicate","payload":payload})
        continue

    r=requests.post(f"{u}/rest/v1/p55a_reproduction_records",headers=h,json=payload)
    if r.status_code>=300:
        skipped.append({"payload":payload,"status":r.status_code,"error":r.text})
    else:
        created+=r.json()

after=requests.get(f"{u}/rest/v1/p55a_reproduction_records?select=id",headers=h).json()

audit={
    "mission":"P5.6A_REPRODUCTION_RECORDS_FROM_EXISTING_PEDIGREE",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "edges_scanned":len(edges),
    "before":len(before),
    "created":len(created),
    "skipped":len(skipped),
    "after":len(after)
}

open("p56a_reproduction_from_pedigree_audit.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))
