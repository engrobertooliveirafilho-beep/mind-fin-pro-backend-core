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
