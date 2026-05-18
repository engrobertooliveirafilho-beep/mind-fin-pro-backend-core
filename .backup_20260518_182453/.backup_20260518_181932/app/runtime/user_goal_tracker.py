def track_goal(user_id, goal, status="active"):
    return {"user_id": user_id, "goal": goal, "status": status, "tracked": True}

def active_goals(user_id):
    return [{"goal": "evoluir MIND/Eldora para operação autônoma", "priority": "P1", "status": "active"}]
