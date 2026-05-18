from app.eldora.core.autonomous_growth_runtime import (
    create_distribution_campaign,
    create_acquisition_swarm,
    execute_commercial_operation,
    optimize_revenue_route
)

def test_distribution():

    r = create_distribution_campaign()

    assert r["status"] == "ok"

def test_swarm():

    r = create_acquisition_swarm()

    assert r["status"] == "ok"

def test_commercial():

    r = execute_commercial_operation(
        "lead_test"
    )

    assert r["status"] == "ok"

def test_optimization():

    r = optimize_revenue_route()

    assert r["status"] == "ok"
