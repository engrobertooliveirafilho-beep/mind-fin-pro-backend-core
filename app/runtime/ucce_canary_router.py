import os, hashlib

CANARY_ENABLED=os.getenv("UCCE_CANARY_ENABLED","false").lower()=="true"
CANARY_PERCENT=int(os.getenv("UCCE_CANARY_PERCENT","10"))
ALLOWLIST=set(filter(None,os.getenv("UCCE_CANARY_ALLOWLIST","").split(",")))

def should_use_ucce(sender_id:str)->bool:
    if not CANARY_ENABLED:
        return False

    sender=(sender_id or "").strip()

    if sender in ALLOWLIST:
        return True

    bucket=int(hashlib.md5(sender.encode()).hexdigest(),16)%100
    return bucket < CANARY_PERCENT
