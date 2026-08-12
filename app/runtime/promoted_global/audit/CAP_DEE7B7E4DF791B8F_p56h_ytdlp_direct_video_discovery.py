import os,json,subprocess,hashlib,datetime,requests

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"}

animals=requests.get(f"{u}/rest/v1/p55a_animals?select=id,official_name&limit=100",headers=h).json()
created=[]; errors=[]

for a in animals:
    q=f"ytsearch5:{a['official_name']} PBR bull ride"
    try:
        p=subprocess.run(["yt-dlp","--dump-json","--flat-playlist",q],capture_output=True,text=True,timeout=60)
        for line in p.stdout.splitlines():
            if not line.strip(): continue
            d=json.loads(line)
            vid=d.get("id")
            title=d.get("title") or ""
            if not vid: continue
            url="https://www.youtube.com/watch?v="+vid
            eh=hashlib.sha256(json.dumps({"animal":a["id"],"url":url},sort_keys=True).encode()).hexdigest()
            payload={
                "animal_id":a["id"],
                "url":url,
                "platform":"youtube",
                "title":title,
                "source_type":"YOUTUBE_DIRECT_SEARCH",
                "raw_payload":{"mission":"P5.6H_YTDLP_DIRECT_VIDEO_DISCOVERY","animal_name":a["official_name"]},
                "confidence_score":55,
                "validation_status":"provisional",
                "evidence_hash":eh
            }
            r=requests.post(f"{u}/rest/v1/p55a_media?on_conflict=evidence_hash",headers=h,json=payload)
            if r.status_code<300: created+=r.json()
            else: errors.append({"animal":a["official_name"],"error":r.text})
    except Exception as e:
        errors.append({"animal":a["official_name"],"error":str(e)})

audit={"mission":"P5.6H_YTDLP_DIRECT_VIDEO_DISCOVERY","created_at":datetime.datetime.now(datetime.UTC).isoformat(),"animals":len(animals),"media_created":len(created),"errors":len(errors)}
open("p56h_ytdlp_direct_video_discovery.json","w",encoding="utf-8").write(json.dumps({"audit":audit,"errors":errors[:20]},ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))
