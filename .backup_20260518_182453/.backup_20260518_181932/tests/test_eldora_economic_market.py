from app.eldora.core.realtime_task_market import (
    create_market_task,
    submit_agent_bid,
    assign_execution_contract
)

def test_market_task():
    r = create_market_task("optimize_runtime")
    assert r["status"] == "ok"

def test_market_bid():

    task = create_market_task("optimize_memory")

    task_id = task["task"]["task_id"]

    bid = submit_agent_bid(
        task_id,
        "agent_alpha"
    )

    assert bid["status"] == "ok"

def test_contract_assignment():

    task = create_market_task("optimize_swarm")

    task_id = task["task"]["task_id"]

    submit_agent_bid(
        task_id,
        "agent_beta",
        5,
        1
    )

    r = assign_execution_contract(task_id)

    assert r["status"] == "ok"
