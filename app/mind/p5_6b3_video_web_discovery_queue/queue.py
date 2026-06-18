import os, json, urllib.request, urllib.parse, hashlib

VIDEO_TERMS=["youtube.com","youtu.be","vimeo.com",".mp4",".mov",".avi",".mkv"]

def h(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def classify_video_url(url):
    u=(url or "").lower()
    if "youtube.com" in u or "youtu.be" in u:
        return "YOUTUBE_METADATA_ONLY_PENDING_AUTHORIZATION"
    if any(u.endswith(ext) or ext in u for ext in [".mp4",".mov",".avi",".mkv"]):
        return "DIRECT_VIDEO_CV_ALLOWED"
    if "vimeo.com" in u:
        return "VIMEO_METADATA_ONLY_PENDING_AUTHORIZATION"
    return "VIDEO_CANDIDATE_REVIEW_REQUIRED"

class VideoWebDiscoveryQueue:
    def __init__(self,url=None,key=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not self.url or not self.key: raise RuntimeError("SUPABASE_URL e KEY ausentes")

    def req(self,method,path,payload=None):
        data=json.dumps(payload).encode("utf-8") if payload is not None else None
        r=urllib.request.Request(self.url+path,data=data,headers={"apikey":self.key,"Authorization":f"Bearer {self.key}","Content-Type":"application/json","Prefer":"resolution=merge-duplicates,return=representation"},method=method)
        with urllib.request.urlopen(r,timeout=30) as x:
            body=x.read().decode("utf-8")
            return json.loads(body) if body else []

    def video_sources(self,limit=500):
        rows=self.req("GET",f"/rest/v1/p55a_sources?select=id,source_url,title,raw_payload,source_type,confidence_score&order=created_at.desc&limit={limit}")
        out=[]
        for r in rows:
            text=" ".join([str(r.get("source_url") or ""),str(r.get("title") or ""),json.dumps(r.get("raw_payload") or {},ensure_ascii=False)]).lower()
            if any(t in text for t in VIDEO_TERMS) or "video" in text or "bull ride" in text:
                out.append(r)
        return out

    def promote_to_media_queue(self,source):
        url=source["source_url"]
        status=classify_video_url(url)
        payload={
            "source_url":url,
            "source_type":"VIDEO_DISCOVERY_QUEUE",
            "title":"P5.6B3 video queue: "+str(source.get("title") or url)[:180],
            "platform":"video_queue",
            "raw_payload":{"mission":"P5.6B3","parent_source_id":source["id"],"video_status":status,"original":source},
            "confidence_score":55,
            "validation_status":"provisional",
            "evidence_hash":h({"mission":"P5.6B3","url":url,"status":status})
        }
        return self.req("POST","/rest/v1/p55a_sources?on_conflict=evidence_hash",payload)[0]

    def run_once(self,limit=500):
        sources=self.video_sources(limit)
        rows=[self.promote_to_media_queue(s) for s in sources]
        by_status={}
        for r in rows:
            st=(r.get("raw_payload") or {}).get("video_status","unknown")
            by_status[st]=by_status.get(st,0)+1
        return {"status":"P5.6B3_VIDEO_WEB_DISCOVERY_QUEUE_DONE","video_candidates":len(sources),"queued":len(rows),"by_status":by_status,"next_action":"P5.6B4_AUTHORIZED_VIDEO_FETCHER"}
