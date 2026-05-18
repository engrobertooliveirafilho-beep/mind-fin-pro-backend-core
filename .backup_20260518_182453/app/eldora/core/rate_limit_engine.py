import time
WINDOWS={}
def check_rate_limit(key: str, limit: int=60, window_seconds: int=60):
    now=int(time.time()); bucket=[t for t in WINDOWS.get(key,[]) if now-t<window_seconds]; allowed=len(bucket)<limit
    if allowed: bucket.append(now)
    WINDOWS[key]=bucket; return {"allowed":allowed,"count":len(bucket),"limit":limit,"window_seconds":window_seconds}
