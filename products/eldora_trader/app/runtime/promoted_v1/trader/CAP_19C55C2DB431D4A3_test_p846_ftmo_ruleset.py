from pathlib import Path
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config, validate_ftmo_config, save_default_ftmo_config, load_ftmo_config, audit_rule_application

def test_default_config_valid():
    r=validate_ftmo_config(default_ftmo_config())
    assert r["valid"] is True
    assert r["reason"]=="FTMO_CONFIG_OK"
    assert len(r["hash"])==64

def test_missing_field_invalid():
    c=default_ftmo_config()
    c.pop("account_size")
    r=validate_ftmo_config(c)
    assert r["valid"] is False
    assert r["reason"]=="MISSING_FIELDS"

def test_invalid_loss_limits_blocked():
    c=default_ftmo_config()
    c["max_daily_loss"]=20000
    c["max_total_loss"]=10000
    r=validate_ftmo_config(c)
    assert r["reason"]=="DAILY_LOSS_GT_TOTAL_LOSS"

def test_save_and_load_config(tmp_path):
    p=tmp_path/"ftmo.json"
    save_default_ftmo_config(str(p))
    cfg,val=load_ftmo_config(str(p))
    assert val["valid"] is True
    assert cfg["version"]=="P8.46_FTMO_RULESET_V1"

def test_missing_config_file_blocks(tmp_path):
    cfg,val=load_ftmo_config(str(tmp_path/"missing.json"))
    assert cfg is None
    assert val["reason"]=="CONFIG_FILE_NOT_FOUND"

def test_audit_rule_application_allows_valid_simulation(tmp_path):
    trade={"symbol":"WIN","daily_trades":1,"daily_pnl":0,"total_pnl":0,"risk_amount":500,"stop":98}
    r=audit_rule_application(trade,default_ftmo_config(),str(tmp_path/"audit.json"))
    assert r["decision"]=="ALLOW_FTMO_SIMULATION"
    assert r["production"]=="BLOCKED"

def test_audit_rule_application_blocks_invalid_trade(tmp_path):
    trade={"symbol":"BTC","daily_trades":99,"daily_pnl":-4900,"total_pnl":0,"risk_amount":500,"stop":None}
    r=audit_rule_application(trade,default_ftmo_config(),str(tmp_path/"audit.json"))
    assert r["decision"]=="BLOCK_FTMO_SIMULATION"
    assert r["edge_claim"]=="NONE"
