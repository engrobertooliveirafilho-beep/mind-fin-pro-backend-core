import os,json,hashlib,datetime,requests

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"}

seed_names=[
    "Mossy Oak Mudslinger",
    "Dillinger",
    "Chicken on a Chain",
    "Blueberry Wine",
    "Voodoo Child",
    "Code Blue",
    "Pandora's Box",
    "High Chaparral",
    "Smooth Operator",
    "SweetPro's Bruiser",
    "Air Time",
    "Big Black",
    "Pearl Harbor",
    "Long John",
    "Shepherd Hills Tested",
    "Crossfire Hurricane",
    "Bushwacker Jr",
    "Fire & Smoke",
    "I’m A Gangster Too",
    "Spotted Demon"
]

created=[]
skipped=[]

for name in seed_names:
    identity=hashlib.sha256(name.lower().encode()).hexdigest()
    existing=requests.get(f"{u}/rest/v1/p55a_animals?select=id,official_name&identity_key=eq.{identity}",headers=h).json()
    if existing:
        skipped.append({"name":name,"reason":"exists","id":existing[0]["id"]})
        continue
    payload={
        "official_name":name,
        "aliases":[],
        "animal_type":"bull",
        "country":"United States",
        "life_status":"unknown",
        "notes":"P5.6G manual audited seed expansion for structural discovery unlock",
        "identity_key":identity,
        "confidence_score":70,
        "validation_status":"provisional"
    }
    r=requests.post(f"{u}/rest/v1/p55a_animals?on_conflict=identity_key",headers=h,json=payload)
    if r.status_code<300:
        created+=r.json()
    else:
        skipped.append({"name":name,"status":r.status_code,"error":r.text})

audit={
    "mission":"P5.6G_MANUAL_AUDITED_ANIMAL_SEED_EXPANSION",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "seed_count":len(seed_names),
    "created":len(created),
    "skipped":len(skipped),
    "created_names":[x.get("official_name") for x in created],
    "skipped_items":skipped
}

open("p56g_manual_audited_animal_seed_expansion.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))
