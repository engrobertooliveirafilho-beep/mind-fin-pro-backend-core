import pytest

from app.runtime.trader_symbol_lineage_contract import (
    SymbolLineageError, propagate_dispatch_symbol, validate_writer_symbol,
)


def test_replay_to_dispatch_to_writer():
    replay = {"symbol": "XAUUSD", "tick": 9}
    dispatch = propagate_dispatch_symbol(replay, {"tick": 9})
    assert dispatch == {"tick": 9, "symbol": "XAUUSD"}
    assert validate_writer_symbol(dispatch, {"symbol": "XAUUSD"}) == "XAUUSD"
    assert "symbol" not in replay


@pytest.mark.parametrize("symbol", [None, "", " XAUUSD", "XAUUSD ", "XAU/USD", 7])
def test_reject_missing_or_invalid_replay_symbol(symbol):
    with pytest.raises(SymbolLineageError):
        propagate_dispatch_symbol({"symbol": symbol}, {})


def test_reject_dispatch_conflict():
    with pytest.raises(SymbolLineageError, match="S21_DISPATCH_SYMBOL_CONFLICT"):
        propagate_dispatch_symbol({"symbol": "XAUUSD"}, {"symbol": "EURUSD"})


def test_reject_writer_conflict():
    with pytest.raises(SymbolLineageError, match="S21_WRITER_SYMBOL_CONFLICT"):
        validate_writer_symbol({"symbol": "XAUUSD"}, {"symbol": "EURUSD"})


def test_reject_writer_missing_symbol():
    with pytest.raises(SymbolLineageError, match="S21_DISPATCH_SYMBOL_MISSING"):
        validate_writer_symbol({}, {"symbol": "XAUUSD"})


@pytest.mark.parametrize("symbol", [" XAUUSD", "XAUUSD ", "XAU/USD", "XAU USD", "é", ""])
def test_writer_rejects_invalid_symbol_even_when_equal(symbol):
    with pytest.raises(SymbolLineageError):
        validate_writer_symbol({"symbol": symbol}, {"symbol": symbol})


def test_symbolized_writer_row_preserves_lineage_and_sources():
    from app.runtime.trader_symbol_lineage_contract import build_symbolized_decision_row
    replay = {"symbol": "XAUUSD", "day": 2, "tick": 3}
    dispatch = {"day": 2, "tick": 3}
    decision = {"symbol": "XAUUSD", "day": 2, "tick": 3, "direction": "BUY"}
    assert build_symbolized_decision_row(replay, dispatch, decision) == decision
    assert "symbol" not in dispatch


@pytest.mark.parametrize("tick", [-1, None, True, 1.5, "1"])
def test_symbolized_writer_row_rejects_invalid_tick(tick):
    from app.runtime.trader_symbol_lineage_contract import build_symbolized_decision_row
    with pytest.raises(SymbolLineageError, match="S21_REPLAY_IDENTITY_INVALID"):
        build_symbolized_decision_row(
            {"symbol": "XAUUSD", "day": 1, "tick": tick},
            {"day": 1, "tick": tick},
            {"symbol": "XAUUSD", "day": 1, "tick": tick},
        )


def test_symbolized_writer_row_rejects_dispatch_day_conflict():
    from app.runtime.trader_symbol_lineage_contract import build_symbolized_decision_row
    with pytest.raises(SymbolLineageError, match="S21_LINEAGE_IDENTITY_CONFLICT"):
        build_symbolized_decision_row(
            {"symbol": "XAUUSD", "day": 1, "tick": 1},
            {"day": 2, "tick": 1},
            {"symbol": "XAUUSD", "day": 1, "tick": 1},
        )


@pytest.mark.parametrize("field", ["day", "tick"])
@pytest.mark.parametrize("alias", [True, 1.0])
@pytest.mark.parametrize("stage", ["dispatch", "decision"])
def test_reject_python_numeric_identity_aliases(field, alias, stage):
    from app.runtime.trader_symbol_lineage_contract import build_symbolized_decision_row
    replay = {"symbol": "XAUUSD", "day": 1, "tick": 1}
    dispatch = {"day": 1, "tick": 1}
    decision = {"symbol": "XAUUSD", "day": 1, "tick": 1}
    (dispatch if stage == "dispatch" else decision)[field] = alias
    with pytest.raises(SymbolLineageError, match="S21_LINEAGE_IDENTITY_CONFLICT"):
        build_symbolized_decision_row(replay, dispatch, decision)
