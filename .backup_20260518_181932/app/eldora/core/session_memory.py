SESSIONS={}
def save_session(user_id: str, tenant_id: str="default", data: dict|None=None):
    SESSIONS[f"{tenant_id}:{user_id}"]={"user_id":user_id,"tenant_id":tenant_id,"data":data or {}}; return SESSIONS[f"{tenant_id}:{user_id}"]
def get_session(user_id: str, tenant_id: str="default"):
    return SESSIONS.get(f"{tenant_id}:{user_id}", {"user_id":user_id,"tenant_id":tenant_id,"data":{},"status":"new"})
