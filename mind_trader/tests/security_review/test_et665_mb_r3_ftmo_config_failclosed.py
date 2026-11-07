"""ET665.MB.R3: malformed FTMO rulesets must not authorize PAPER execution."""
import json
import math
import pytest
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config, validate_ftmo_config, load_ftmo_config

@pytest.mark.parametrize("config", [None, [], "", 42, True])
def test_non_mapping_config_is_rejected(config):
    assert validate_ftmo_config(config)["valid"] is False

@pytest.mark.parametrize("field", ["account_size", "profit_target", "max_daily_loss", "max_total_loss", "commission", "spread", "slippage", "max_position_size"])
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), True])
def test_nonfinite_or_boolean_numeric_fields_are_rejected(field, bad):
    cfg = default_ftmo_config()
    cfg[field] = bad
    result = validate_ftmo_config(cfg)
    assert result["valid"] is False

@pytest.mark.parametrize("text", ["{bad json", "null", "[]", '"text"'])
def test_corrupt_config_file_fails_closed(tmp_path, text):
    path = tmp_path / "ftmo.json"
    path.write_text(text, encoding="utf-8")
    cfg, validation = load_ftmo_config(str(path))
    assert validation["valid"] is False

def test_default_config_still_valid():
    assert validate_ftmo_config(default_ftmo_config())["valid"] is True
