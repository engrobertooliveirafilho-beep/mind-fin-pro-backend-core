from app.runtime.p2223_broker_emulator import run_simulation

def test_broker_emulator():
    r = run_simulation(20)
    assert r["status"] == "PASS"
    assert r["mode"] == "BROKER_EMULATOR_SIMULATION_ONLY"
    assert r["total_trades"] > 0
