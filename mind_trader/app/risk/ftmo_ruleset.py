import json, hashlib, math
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
    if not isinstance(config, dict):
        return {"valid": False, "reason": "INVALID_CONFIG_TYPE"}
    missing=[k for k in REQUIRED_FIELDS if k not in config]
    if missing:
        return {"valid":False,"reason":"MISSING_FIELDS","missing":missing}
    type_errors=[k for k,t in REQUIRED_FIELDS.items() if not isinstance(config[k],t)]
    if type_errors:
        return {"valid":False,"reason":"TYPE_ERRORS","fields":type_errors}
    numeric_fields = [key for key, expected in REQUIRED_FIELDS.items() if expected == (int,float) or expected is int]
    invalid_numeric = [
        key for key in numeric_fields
        if isinstance(config[key], bool) or not math.isfinite(config[key])
    ]
    if invalid_numeric:
        return {"valid": False, "reason": "INVALID_NUMERIC_VALUES", "fields": invalid_numeric}
    numeric_positive=["account_size","profit_target","max_daily_loss","max_total_loss","minimum_trading_days","max_daily_trades","leverage"]
    invalid=[k for k in numeric_positive if config[k] <= 0]
    if invalid:
        return {"valid":False,"reason":"INVALID_NUMERIC_LIMITS","fields":invalid}
    nonnegative_costs = ("commission", "spread", "slippage")
    invalid_costs = [key for key in nonnegative_costs if config[key] < 0]
    if invalid_costs:
        return {"valid":False,"reason":"INVALID_TRADING_COSTS","fields":invalid_costs}
    if config["max_position_size"] <= 0:
        return {"valid":False,"reason":"INVALID_POSITION_SIZE"}
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
    try:
        cfg=json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None, {"valid": False, "reason": "CONFIG_READ_OR_PARSE_FAILED"}
    return cfg, validate_ftmo_config(cfg)

def audit_rule_application(trade, config, path="mind_trader/reports/P8.46_ftmo_rule_audit.json"):
    validation = validate_ftmo_config(config)
    valid_trade = isinstance(trade, dict)
    checks = {
        "symbol_allowed": False,
        "symbol_not_restricted": False,
        "daily_trades_ok": False,
        "risk_inside_daily_limit": False,
        "risk_inside_total_limit": False,
        "has_stop": False,
    }
    if validation["valid"] and valid_trade:
        numeric = ("daily_trades", "daily_pnl", "total_pnl", "risk_amount")
        values = {key: trade.get(key, 0) for key in numeric}
        valid_numbers = all(
            not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value) for value in values.values()
        )
        valid_numbers = valid_numbers and type(values["daily_trades"]) is int
        valid_numbers = valid_numbers and values["daily_trades"] >= 0 and values["risk_amount"] > 0
        symbol = trade.get("symbol")
        allowed = config["allowed_symbols"]
        restricted = config["restricted_symbols"]
        valid_symbols = (
            isinstance(symbol, str) and bool(symbol.strip())
            and all(isinstance(item, str) for item in allowed + restricted)
        )
        if valid_symbols:
            checks["symbol_allowed"] = symbol in allowed
            checks["symbol_not_restricted"] = symbol not in restricted
        if valid_numbers:
            checks["daily_trades_ok"] = values["daily_trades"] < config["max_daily_trades"]
            daily_exposure = abs(values["daily_pnl"]) + values["risk_amount"]
            total_exposure = abs(values["total_pnl"]) + values["risk_amount"]
            checks["risk_inside_daily_limit"] = (
                math.isfinite(daily_exposure) and daily_exposure <= config["max_daily_loss"]
            )
            checks["risk_inside_total_limit"] = (
                math.isfinite(total_exposure) and total_exposure <= config["max_total_loss"]
            )
        stop = trade.get("stop")
        checks["has_stop"] = (
            not isinstance(stop, bool) and isinstance(stop, (int, float))
            and math.isfinite(stop) and stop > 0
        )
    report = {
        "audit_ts": datetime.now(UTC).isoformat(),
        "config_validation": validation,
        "config_hash": validation.get("hash"),
        "config_version": config.get("version") if isinstance(config, dict) else None,
        "trade_input_type": type(trade).__name__,
        "checks": checks,
        "production": "BLOCKED",
        "edge_claim": "NONE",
    }
    report["decision"] = (
        "ALLOW_FTMO_SIMULATION"
        if validation["valid"] and valid_trade and all(checks.values())
        else "BLOCK_FTMO_SIMULATION"
    )
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
