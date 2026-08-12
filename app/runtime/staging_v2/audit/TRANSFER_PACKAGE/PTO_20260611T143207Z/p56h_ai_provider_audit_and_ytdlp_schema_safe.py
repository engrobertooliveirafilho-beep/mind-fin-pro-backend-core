import os,json,subprocess,datetime,requests

u=os.getenv("SUPABASE_URL").rstrip("/")
k=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
h={"apikey":k,"Authorization":"Bearer "+k,"Content-Type":"application/json","Prefer":"return=representation"}

ai_keys={x:bool(os.getenv(x)) for x in [
"OPENAI_API_KEY","ANTHROPIC_API_KEY","GEMINI_API_KEY","GOOGLE_API_KEY",
"PERPLEXITY_API_KEY","MISTRAL_API_KEY","GROQ_API_KEY","SERPAPI_KEY",
"SEARCH_API_KEY","BRAVE_SEARCH_API_KEY","BING_SEARCH_API_KEY"
]}

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
                "validation_status":"provisional",
                "raw_payload":{"mission":"P5.6H_YTDLP_DIRECT_VIDEO_DISCOVERY_SCHEMA_SAFE","animal_name":a["official_name"]}
            }
            r=requests.post(f"{u}/rest/v1/p55a_media",headers=h,json=payload)
            if r.status_code<300: created+=r.json()
            else: errors.append({"animal":a["official_name"],"url":url,"error":r.text})
    except Exception as e:
        errors.append({"animal":a["official_name"],"error":str(e)})

audit={
 "mission":"P5.6H_AI_PROVIDER_AUDIT_AND_SCHEMA_SAFE_YTDLP_DISCOVERY",
 "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
 "ai_keys_available":ai_keys,
 "animals_scanned":len(animals),
 "media_created":len(created),
 "skipped_existing":len(skipped),
 "errors":len(errors)
}

open("p56h_ai_provider_audit_and_ytdlp_schema_safe.json","w",encoding="utf-8").write(json.dumps({"audit":audit,"errors":errors[:30]},ensure_ascii=False,indent=2))
print(json.dumps(audit,indent=2,ensure_ascii=False))
