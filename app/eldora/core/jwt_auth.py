import os, base64, json, hmac, hashlib, time
def _secret(): return os.getenv("ELDORA_JWT_SECRET", "dev-only-change-me")
def _b64(data: bytes): return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
def _unb64(data: str): return base64.urlsafe_b64decode((data + "=" * (-len(data) % 4)).encode())
def create_token(user_id: str, tenant_id: str="default", role: str="user", ttl_seconds: int=3600):
    h=_b64(json.dumps({"alg":"HS256","typ":"JWT"}).encode()); p=_b64(json.dumps({"sub":user_id,"tenant_id":tenant_id,"role":role,"exp":int(time.time())+ttl_seconds}).encode())
    s=_b64(hmac.new(_secret().encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()); return f"{h}.{p}.{s}"
def verify_token(token: str):
    try:
        h,p,s=token.split("."); e=_b64(hmac.new(_secret().encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(s,e): return {"valid":False,"reason":"bad_signature"}
        payload=json.loads(_unb64(p)); return {"valid": payload.get("exp",0) >= int(time.time()), "payload": payload}
    except Exception as e: return {"valid":False,"reason":str(e)}
