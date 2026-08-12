import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_FIELDS = {
    "version": str,
    "account_size": (int,float),
    "profit_target": (int,float),
    "max_daily_loss": (int,float),
    "max_total_loss": (int,float),
    "minimum_trading_days": int,
    "max_position_size": (int,float),
    "max_daily_trades": int,
    "allowed_symbols": list,
    "restricted_symbols": list,
    "allowed_sessions": list,
    "restricted_news_events": bool,
    "commission": (int,float),
    "spread": (int,float),
    "slippage": (int,float),
    "leverage": int,
    "platform": str,
    "challenge_type": str,
    "phase": str
}

def default_ftmo_config():
    return {
        "version":"P8.46_FTMO_RULESET_V1",
        "account_size":100000,
        "profit_target":10000,
        "max_daily_loss":5000,
        "max_total_loss":10000,
        "minimum_trading_days":4,
        "max_position_size":1.0,
        "max_daily_trades":5,
        "allowed_symbols":["WIN","WDO","EURUSD","XAUUSD"],
        "restricted_symbols":[],
        "allowed_sessions":["09:00-17:00"],
        "restricted_news_events":True,
        "commission":0.0,
        "spread":0.0,
        "slippage":0.0,
        "leverage":100,
        "platform":"MT5",
        "challenge_type":"evaluation",
        "phase":"simulation"
    }

def config_hash(config):
    raw=json.dumps(config,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def validate_ftmo_config(config):
    missing=[k for k in REQUIRED_FIELDS if k not in config]
    if missing:
        return {"valid":False,"reason":"MISSING_FIELDS","missing":missing}
    type_errors=[k for k,t in REQUIRED_FIELDS.items() if not isinstance(config[k],t)]
    if type_errors:
        return {"valid":False,"reason":"TYPE_ERRORS","fields":type_errors}
    numeric_positive=["account_size","profit_target","max_daily_loss","max_total_loss","minimum_trading_days","max_daily_trades","leverage"]
    invalid=[k for k in numeric_positive if config[k] <= 0]
    if invalid:
        return {"valid":False,"reason":"INVALID_NUMERIC_LIMITS","fields":invalid}
    if config["max_daily_loss"] > config["max_total_loss"]:
        return {"valid":False,"reason":"DAILY_LOSS_GT_TOTAL_LOSS"}
    if not config["allowed_symbols"]:
        return {"valid":False,"reason":"NO_ALLOWED_SYMBOLS"}
    return {"valid":True,"reason":"FTMO_CONFIG_OK","hash":config_hash(config),"version":config["version"]}

def save_default_ftmo_config(path="mind_trader/config/ftmo_ruleset.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    cfg=default_ftmo_config()
    Path(path).write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding="utf-8")
    return path

def load_ftmo_config(path="mind_trader/config/ftmo_ruleset.json"):
    p=Path(path)
    if not p.exists():
        return None, {"valid":False,"reason":"CONFIG_FILE_NOT_FOUND"}
    cfg=json.loads(p.read_text(encoding="utf-8"))
    return cfg, validate_ftmo_config(cfg)

def audit_rule_application(trade, config, path="mind_trader/reports/P8.46_ftmo_rule_audit.json"):
    validation=validate_ftmo_config(config)
    report={
        "audit_ts":datetime.now(UTC).isoformat(),
        "config_validation":validation,
        "config_hash":validation.get("hash"),
        "config_version":config.get("version"),
        "trade":trade,
        "checks":{
            "symbol_allowed":trade.get("symbol") in config.get("allowed_symbols",[]),
            "symbol_not_restricted":trade.get("symbol") not in config.get("restricted_symbols",[]),
            "daily_trades_ok":trade.get("daily_trades",0) < config.get("max_daily_trades",0),
            "risk_inside_daily_limit":abs(trade.get("daily_pnl",0))+trade.get("risk_amount",0) <= config.get("max_daily_loss",0),
            "risk_inside_total_limit":abs(trade.get("total_pnl",0))+trade.get("risk_amount",0) <= config.get("max_total_loss",0),
            "has_stop":trade.get("stop") is not None
        },
        "production":"BLOCKED",
        "edge_claim":"NONE"
    }
    report["decision"]="ALLOW_FTMO_SIMULATION" if validation["valid"] and all(report["checks"].values()) else "BLOCK_FTMO_SIMULATION"
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
