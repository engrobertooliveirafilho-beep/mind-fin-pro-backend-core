import os, json, urllib.request, urllib.parse, hashlib, re

def is_youtube_watch(url):
    u=(url or "").lower()
    return ("youtube.com/watch" in u and "v=" in u) or "youtu.be/" in u

def h(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

class YouTubeURLResolver:
    def __init__(self,url=None,key=None,search_key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        self.search_key=search_key or os.getenv("SERPAPI_KEY") or os.getenv("SEARCH_API_KEY")
        if not self.url or not self.key: raise RuntimeError("SUPABASE_URL e KEY ausentes")
        if not self.search_key: raise RuntimeError("SERPAPI_KEY ou SEARCH_API_KEY ausente")

    def req(self,method,path,payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def search_media(self,limit=25):
        return self.req("GET",f"/rest/v1/p55a_media?platform=eq.youtube&select=id,animal_id,url,title,metadata&limit={limit}")

    def serpapi_youtube(self,query):
        api="https://serpapi.com/search.json?engine=youtube&search_query="+urllib.parse.quote(query)+"&api_key="+urllib.parse.quote(self.search_key)
        with urllib.request.urlopen(api,timeout=45) as r:
            data=json.loads(r.read().decode("utf-8"))
        return data.get("video_results",[])[:10]

    def upsert_media_watch_url(self,parent,video):
        link=video.get("link") or video.get("url")
        if not is_youtube_watch(link):
            return None
        payload={
            "animal_id":parent["animal_id"],
            "url":link,
            "platform":"youtube",
            "title":video.get("title") or parent.get("title"),
            "event_name":"P5.6B5 resolved YouTube video",
            "result":"resolved_watch_url",
            "metadata":{"mission":"P5.6B5","parent_media_id":parent["id"],"source":"serpapi_youtube","video":video},
            "confidence_score":65,
            "validation_status":"provisional"
        }
        existing=self.req("GET","/rest/v1/p55a_media?url=eq."+urllib.parse.quote(link,safe="")+"&select=id,animal_id,url,title")
        if existing: return existing[0]
        return self.req("POST","/rest/v1/p55a_media",payload)[0]

    def run_once(self,limit=10):
        parents=self.search_media(limit)
        created=[]; skipped=0
        for p in parents:
            if is_youtube_watch(p["url"]):
                skipped+=1
                continue
            query=(p.get("title") or "") + " bull ride"
            results=self.serpapi_youtube(query)
            for v in results[:3]:
                row=self.upsert_media_watch_url(p,v)
                if row: created.append(row)
        return {"status":"P5.6B5_YOUTUBE_URL_RESOLVER_DONE","parents_scanned":len(parents),"watch_urls_created_or_seen":len(created),"skipped_watch_existing":skipped,"next_action":"RERUN_P5.6B4_ON_WATCH_URLS"}
