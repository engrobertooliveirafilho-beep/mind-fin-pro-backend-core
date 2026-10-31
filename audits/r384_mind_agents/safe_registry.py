"""Registry-based proposal builder, without import-time side effects."""
def build_proposal(agent_id, registry):
    if agent_id not in registry:
        raise ValueError("UNKNOWN_AGENT")
    fields = registry[agent_id].get("fields", [])
    if not fields:
        raise ValueError("MISSING_SCHEMA")
    return {"agent_id": agent_id, "status": "draft_unverified", "fields": {name: None for name in fields}}
