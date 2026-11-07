"""ET665.MB.R7: FTMO cost limits must agree with PAPER fill validation."""
import pytest
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config, validate_ftmo_config, load_ftmo_config

@pytest.mark.parametrize("field", ["spread", "slippage", "commission"])
def test_negative_cost_rejected_by_ruleset(field):
    cfg = default_ftmo_config()
    cfg[field] = -0.01
    result = validate_ftmo_config(cfg)
    assert result["valid"] is False
    assert result["reason"] == "INVALID_TRADING_COSTS"

@pytest.mark.parametrize("size", [0, -1.0])
def test_nonpositive_position_size_rejected(size):
    cfg = default_ftmo_config()
    cfg["max_position_size"] = size
    assert validate_ftmo_config(cfg)["reason"] == "INVALID_POSITION_SIZE"

def test_zero_costs_still_valid():
    assert validate_ftmo_config(default_ftmo_config())["valid"] is True

def test_invalid_costs_fail_closed_when_loaded(tmp_path):
    cfg = default_ftmo_config()
    cfg["spread"] = -0.1
    path = tmp_path / "ftmo.json"
    import json
    path.write_text(json.dumps(cfg), encoding="utf-8")
    _, result = load_ftmo_config(str(path))
    assert result["valid"] is False
