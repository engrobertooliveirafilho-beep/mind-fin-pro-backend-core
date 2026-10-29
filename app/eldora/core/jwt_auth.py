import os, base64, json, hmac, hashlib, time

def _secret():
    secret = os.getenv("ELDORA_JWT_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("ELDORA_JWT_SECRET must contain at least 32 UTF-8 bytes")
    return secret

def _b64(data: bytes):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _unb64(data: str):
    return base64.urlsafe_b64decode((data + "=" * (-len(data) % 4)).encode())

def create_token(user_id: str, tenant_id: str="default", role: str="user", ttl_seconds: int=3600):
    if not user_id or user_id == "anonymous" or not tenant_id or not role or not 0 < ttl_seconds <= 3600:
        raise ValueError("Invalid token claims")
    h = _b64(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
    p = _b64(json.dumps({"sub":user_id,"tenant_id":tenant_id,"role":role,"exp":int(time.time())+ttl_seconds}).encode())
    s = _b64(hmac.new(_secret().encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{s}"

def verify_token(token: str):
    try:
        h,p,s = token.split(".")
        header = json.loads(_unb64(h))
        if header != {"alg":"HS256","typ":"JWT"}:
            return {"valid":False,"reason":"invalid_header"}
        expected = _b64(hmac.new(_secret().encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(s, expected):
            return {"valid":False,"reason":"bad_signature"}
        payload = json.loads(_unb64(p))
        if not isinstance(payload, dict) or not all(isinstance(payload.get(k), str) and payload[k] for k in ("sub","tenant_id","role")):
            return {"valid":False,"reason":"invalid_claims"}
        exp = payload.get("exp")
        if not isinstance(exp, int) or isinstance(exp, bool) or exp <= int(time.time()):
            return {"valid":False,"reason":"expired"}
        return {"valid":True,"payload":payload}
    except (ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError):
        return {"valid":False,"reason":"invalid_token"}
