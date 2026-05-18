from .boundaries import can_send
from .greeting_engine import build_greeting
def plan_checkin(profile, memory=None):
    ok, reason = can_send(profile)
    if not ok: return {"send":False,"reason":reason}
    return {"send":True,"reason":"OK","message":build_greeting(profile.get("name","Roberto"), memory)}
