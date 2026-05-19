from __future__ import annotations
import time, hashlib

_CACHE={}

def should_block_duplicate(sender_id:str,response:str,window:int=10)->bool:
    now=time.time()
    key=f"{sender_id}:{hashlib.md5((response or '').encode()).hexdigest()}"
    last=_CACHE.get(key)
    _CACHE[key]=now
    return last is not None and (now-last)<=window
