PLANS = {
    "free": {"messages_per_day": 20, "premium": False},
    "starter": {"messages_per_day": 200, "premium": True},
    "premium": {"messages_per_day": 1000, "premium": True},
    "enterprise": {"messages_per_day": 10000, "premium": True},
}

def resolve_plan(plan: str | None) -> dict:
    key = plan if plan in PLANS else "free"
    return {"plan": key, "limits": PLANS[key]}

def enforce_plan_limits(plan: str, usage: int) -> dict:
    resolved = resolve_plan(plan)
    limit = resolved["limits"]["messages_per_day"]
    return {"plan": resolved["plan"], "usage": usage, "limit": limit, "allowed": usage < limit}
