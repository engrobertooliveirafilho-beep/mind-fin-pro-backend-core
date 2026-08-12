import csv, json
from pathlib import Path

P2389 = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
P2388 = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2388_DE40_PAPER_FORWARD_MONITOR_20260624_180202")
P2387 = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2387_DE40_MT5_PAPER_BRIDGE_VALIDATION_20260624_175907")
P2386B = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2386B_SIGNAL_BUS_SCHEMA_REPAIR_20260624_175427")
OUT = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2390_DE40_PAPER_ONLY_TEST_SUITE_20260624_215627")

def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        delimiter = ";" if sample.count(";") >= sample.count(",") else ","
        return list(csv.DictReader(f, delimiter=delimiter))

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def test_governance_lock_certified():
    s = read_json(P2389 / "summary.json")
    assert s["certification"] == "P2389_GOVERNANCE_LOCK_CERTIFIED"
    assert s["mode"] == "PAPER_ONLY"
    assert s["real_orders"] == "FORBIDDEN"
    assert s["ftmo_real"] == "FORBIDDEN"
    assert s["real_execution_allowed"] is False
    assert s["paper_forward_allowed"] is True

def test_policy_blocks_real_execution():
    p = read_json(P2389 / "governance_policy.json")
    assert p["mode"] == "PAPER_ONLY"
    assert p["real_orders"] == "FORBIDDEN"
    assert p["ftmo_real"] == "FORBIDDEN"
    assert p["mt5_real_permission"] == "DENIED"
    assert "REAL_ORDER_SEND" in p["blocked_operations"]
    assert "FTMO_REAL_TRADE" in p["blocked_operations"]

def test_signal_bus_schema_and_locks():
    rows = read_csv(P2386B / "mind_de40_paper_signal_bus_p2386b.csv")
    assert len(rows) == 230

    required = [
        "signal_id","symbol","timeframe","entry_time","direction","mode",
        "execution_permission","paper_permission","real_orders","ftmo_real",
        "mt5_real_permission","ftmo_real_permission","signal_status","warning"
    ]

    for r in rows:
        for c in required:
            assert c in r
        assert r["mode"] == "PAPER_ONLY"
        assert r["real_orders"] == "FORBIDDEN"
        assert r["ftmo_real"] == "FORBIDDEN"
        assert r["mt5_real_permission"] == "DENIED"
        assert r["ftmo_real_permission"] == "DENIED"
        assert r["paper_permission"] == "ALLOW"
        assert r["signal_status"] == "PAPER_SIGNAL_READY"
        assert r["direction"] in ["BUY_PAPER", "SELL_PAPER"]

def test_mt5_bridge_is_paper_only():
    rows = read_csv(P2387 / "mind_de40_mt5_paper_bridge_p2387.csv")
    assert len(rows) == 230

    for r in rows:
        assert r["order_type"] == "PAPER_ONLY_SIMULATION"
        assert r["execution_permission"] == "PAPER_ONLY_FILE_SIGNAL"
        assert r["mt5_real_permission"] == "DENIED"
        assert r["real_orders"] == "FORBIDDEN"
        assert r["ftmo_real"] == "FORBIDDEN"
        assert r["status"] == "MT5_PAPER_BRIDGE_READY"

def test_forward_monitor_certified_and_closed():
    s = read_json(P2388 / "summary.json")
    assert s["certification"] == "P2388_PAPER_FORWARD_MONITOR_CERTIFIED"
    assert s["mode"] == "PAPER_ONLY"
    assert s["real_orders"] == "FORBIDDEN"
    assert s["ftmo_real"] == "FORBIDDEN"
    assert s["real_execution_allowed"] is False
    assert s["input_bridge_signals"] == 230
    assert s["closed"] == 230
    assert s["statistics"]["pf"] >= 1.5
    assert s["statistics"]["expectancy"] > 0
    assert s["statistics"]["winrate"] >= 45

def test_monitor_bus_has_no_real_permission():
    rows = read_csv(P2388 / "mind_de40_paper_monitor_bus.csv")
    assert len(rows) == 230

    for r in rows:
        assert r["mode"] == "PAPER_ONLY"
        assert r["real_orders"] == "FORBIDDEN"
        assert r["ftmo_real"] == "FORBIDDEN"
        assert r["mt5_real_permission"] == "DENIED"
        assert str(r["real_execution_allowed"]).lower() == "false"
        assert r["state"] == "CLOSED"

def test_equity_curve_consistency():
    stats = read_csv(P2388 / "de40_forward_statistics.csv")[0]
    curve = read_csv(P2388 / "de40_forward_equity_curve.csv")
    assert len(curve) == 230

    final_equity = float(curve[-1]["equity_r"])
    net_r = float(stats["net_r"])

    assert abs(final_equity - net_r) < 0.00001

def test_learning_events_observe_only():
    rows = read_csv(P2388 / "de40_forward_learning_events.csv")
    assert len(rows) == 230

    for r in rows:
        assert r["learning_action"] == "OBSERVE_ONLY_NO_AUTOMATIC_RETRAIN"
        assert r["mode"] == "PAPER_ONLY"
        assert r["real_orders"] == "FORBIDDEN"

def test_artifact_existence():
    required = [
        P2389 / "governance_policy.json",
        P2389 / "governance_manifest.json",
        P2389 / "governance_lock_checks.csv",
        P2386B / "mind_de40_paper_signal_bus_p2386b.csv",
        P2387 / "mind_de40_mt5_paper_bridge_p2387.csv",
        P2388 / "mind_de40_paper_monitor_bus.csv",
        P2388 / "de40_forward_statistics.csv",
        P2388 / "de40_forward_equity_curve.csv",
        P2388 / "de40_forward_learning_events.csv",
    ]

    for p in required:
        assert p.exists(), str(p)
        assert p.stat().st_size > 0, str(p)
