def remember_long_term(user_id, event, project="MIND"):
    return {"stored": True, "user_id": user_id, "project": project, "event": event, "memory_type": "longitudinal"}

def retrieve_longitudinal_context(user_id, query):
    return {
        "user_id": user_id,
        "dominant_project": "MIND",
        "active_agent": "Eldora",
        "continuity": "prosseguir evolução com memória, autonomia e execução",
        "query": query
    }
