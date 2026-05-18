from app.eldora.core.browser_fleet_runtime import (
    create_browser_agent,
    create_browser_task,
    assign_browser_task
)

def test_browser_agent():

    r = create_browser_agent(
        "agent_browser_alpha"
    )

    assert r["status"] == "ok"

def test_browser_task():

    r = create_browser_task(
        "scan_market",
        "https://example.com"
    )

    assert r["status"] == "ok"

def test_browser_assignment():

    agent = create_browser_agent(
        "agent_browser_beta"
    )

    task = create_browser_task(
        "scan_competitors",
        "https://example.com"
    )

    r = assign_browser_task(
        task["task"]["task_id"],
        agent["agent"]["agent_id"]
    )

    assert r["status"] == "ok"
