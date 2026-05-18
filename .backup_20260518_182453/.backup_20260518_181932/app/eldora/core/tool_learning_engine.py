from datetime import datetime, timezone

LEARNED_TOOLS = {}

def learn_tool(tool_name: str, capability: str):
    LEARNED_TOOLS[tool_name] = {
        "capability": capability,
        "learned_at": datetime.now(timezone.utc).isoformat()
    }

    return {
        "status": "ok",
        "tool_name": tool_name,
        "capability": capability,
        "tools_total": len(LEARNED_TOOLS)
    }

def tool_report():
    return {
        "status": "ok",
        "tools_total": len(LEARNED_TOOLS),
        "tools": LEARNED_TOOLS
    }
