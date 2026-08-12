import os,json,subprocess,datetime,requests

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"return=representation"}

animals=requests.get(f"{u}/rest/v1/p55a_animals?select=id,official_name&limit=100",headers=h).json()
created=[]; skipped=[]; errors=[]

for a in animals:
    q=f"ytsearch5:{a['official_name']} PBR bull ride"
    try:
        p=subprocess.run(["yt-dlp","--dump-json","--flat-playlist",q],capture_output=True,text=True,timeout=90)
        if p.returncode!=0:
            errors.append({"animal":a["official_name"],"error":(p.stderr or p.stdout)[-800:]})
            continue

        for line in p.stdout.splitlines():
            if not line.strip(): continue
            d=json.loads(line)
            vid=d.get("id")
            title=d.get("title") or ""
            if not vid: continue

            url="https://www.youtube.com/watch?v="+vid
            exists=requests.get(f"{u}/rest/v1/p55a_media?select=id&url=eq.{url}",headers=h).json()
            if exists:
                skipped.append(url)
                continue

            payload={
                "animal_id":a["id"],
                "url":url,
                "platform":"youtube",
                "title":title,
                "source_id":None,
                "confidence_score":55,
                "validation_status":"provisional"
            }

            r=requests.post(f"{u}/rest/v1/p55a_media",headers=h,json=payload)
            if r.status_code<300:
                created+=r.json()
            else:
                errors.append({"animal":a["official_name"],"url":url,"error":r.text})
    except Exception as e:
        errors.append({"animal":a["official_name"],"error":str(e)})

audit={
 "mission":"P5.6H_YTDLP_DIRECT_VIDEO_DISCOVERY_SCHEMA_FIXED",
 "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
 "animals_scanned":len(animals),
 "media_created":len(created),
 "skipped_existing":len(skipped),
 "errors":len(errors)
}

open("p56h_ytdlp_direct_video_discovery_schema_fixed.json","w",encoding="utf-8").write(json.dumps({"audit":audit,"errors":errors[:30]},ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))
