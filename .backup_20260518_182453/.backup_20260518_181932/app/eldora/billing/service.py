def create_subscription(user_id: str, plan: str, provider: str = "mock") -> dict:
    return {"user_id": user_id, "plan": plan, "provider": provider, "subscription_status": "mock_created", "real_revenue": False}

def activate_premium(user_id: str, plan: str) -> dict:
    return {"user_id": user_id, "plan": plan, "premium_active": plan in ("starter", "premium", "enterprise"), "real_revenue": False}
