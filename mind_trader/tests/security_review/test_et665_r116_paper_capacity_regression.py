"""ET665.R116 — SQLite PAPER capacity regression; isolated, no broker/MT5."""
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).with_name("et665_r113_paper_capacity_gate.py")
spec = importlib.util.spec_from_file_location("et665_capacity", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
PaperCapacityGate = module.PaperCapacityGate


def test_reservation_limit_survives_restart(tmp_path):
    path = tmp_path / "capacity.sqlite"
    gate = PaperCapacityGate(path)
    first = gate.reserve_new("session-A", 1)
    assert first["decision"] == "RESERVED"
    restarted = PaperCapacityGate(path)
    assert restarted.reserve_new("session-A", 1)["decision"] == "BLOCK_CAPACITY"
    assert restarted.remaining("session-A", 1) == 0


def test_filled_reservation_keeps_capacity(tmp_path):
    gate = PaperCapacityGate(tmp_path / "capacity.sqlite")
    first = gate.reserve_new("session-A", 1)
    assert gate.finalize("session-A", first["order_id"], True) == "FILLED"
    assert gate.reserve_new("session-A", 1)["decision"] == "BLOCK_CAPACITY"


def test_rejected_reservation_releases_capacity(tmp_path):
    gate = PaperCapacityGate(tmp_path / "capacity.sqlite")
    first = gate.reserve_new("session-A", 1)
    assert gate.finalize("session-A", first["order_id"], False) == "REJECTED"
    assert gate.reserve_new("session-A", 1)["decision"] == "RESERVED"


def test_unknown_or_invalid_requests_fail_closed(tmp_path):
    gate = PaperCapacityGate(tmp_path / "capacity.sqlite")
    assert gate.reserve_new("session-A", True)["decision"] == "BLOCK_INVALID_CAPACITY"
    assert gate.finalize("session-A", "unknown", True) == "BLOCK_UNKNOWN_ORDER"
    assert gate.remaining("session-A", 0) == 0


def test_parallel_reservations_never_exceed_limit(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path = tmp_path / "capacity.sqlite"
    PaperCapacityGate(path)
    def reserve(_):
        return PaperCapacityGate(path).reserve_new("session-A", 3)["decision"]
    with ThreadPoolExecutor(max_workers=8) as pool:
        decisions = list(pool.map(reserve, range(12)))
    assert decisions.count("RESERVED") == 3
    assert decisions.count("BLOCK_CAPACITY") == 9
    assert PaperCapacityGate(path).remaining("session-A", 3) == 0


def test_reserved_capacity_survives_restart_after_unknown_outcome(tmp_path):
    path = tmp_path / "capacity.sqlite"
    gate = PaperCapacityGate(path)
    reservation = gate.reserve_new("session-A", 1)
    assert reservation["decision"] == "RESERVED"
    del gate
    restarted = PaperCapacityGate(path)
    assert restarted.reserve_new("session-A", 1)["decision"] == "BLOCK_CAPACITY"
    assert restarted.finalize("session-A", reservation["order_id"], True) == "FILLED"
    assert PaperCapacityGate(path).reserve_new("session-A", 1)["decision"] == "BLOCK_CAPACITY"


def test_session_capacity_isolated(tmp_path):
    gate = PaperCapacityGate(tmp_path / "capacity.sqlite")
    assert gate.reserve_new("session-A", 1)["decision"] == "RESERVED"
    assert gate.reserve_new("session-B", 1)["decision"] == "RESERVED"
    assert gate.reserve_new("session-A", 1)["decision"] == "BLOCK_CAPACITY"
