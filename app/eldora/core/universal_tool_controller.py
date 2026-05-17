from datetime import datetime, timezone

TOOLS=[]

def register_tool(tool_name:str, capability:str):
    item = {
        "tool_name":tool_name,
        "capability":capability,
        "status":"available",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    TOOLS.append(item)

    return {
        "status":"ok",
        "tool":item
    }

def tool_report():
    return {
        "status":"ok",
        "tools_total":len(TOOLS),
        "tools":TOOLS[-100:]
    }
