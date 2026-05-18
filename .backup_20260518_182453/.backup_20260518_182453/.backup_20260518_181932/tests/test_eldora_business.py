from app.eldora.core.business_runtime import (
    create_business_agent,
    create_lead,
    register_revenue_event
)

def test_business_agent():

    r = create_business_agent(
        "agent_sales_alpha"
    )

    assert r["status"] == "ok"

def test_lead_pipeline():

    r = create_lead(
        "roberto"
    )

    assert r["status"] == "ok"

def test_revenue_event():

    lead = create_lead(
        "enterprise_client"
    )

    lead_id = lead["lead"]["lead_id"]

    r = register_revenue_event(
        lead_id,
        2500.0
    )

    assert r["status"] == "ok"
