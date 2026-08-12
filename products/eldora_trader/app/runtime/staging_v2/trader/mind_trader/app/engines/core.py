from dataclasses import dataclass, asdict
from datetime import datetime, UTC
import json, uuid, os

@dataclass
class FTMOConfig:
    account_size: float = 100000
    profit_target: float = 10000
    max_daily_loss: float = 5000
    max_total_loss: float = 10000
    max_daily_trades: int = 5
    allowed_symbols: tuple = ("WIN","WDO","EURUSD","XAUUSD")
    restricted_symbols: tuple = ()
    restricted_news_events: bool = True

@dataclass
class TradeIntent:
    mode: str
    symbol: str
    strategy_id: str
    regime: str
    entry: float
    stop: float | None
    target: float
    risk_amount: float
    open_risk: float
    daily_pnl: float
    total_pnl: float
    daily_trades: int
    loss_streak: int
    session_allowed: bool = True
    news_blocked: bool = False

class Ledger:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
    def write(self, event):
        event["id"] = str(uuid.uuid4())
        event["ts"] = datetime.now(UTC).isoformat()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

class RiskGuardian:
    def validate(self, trade):
        if trade.stop is None: return False, "NO_STOP_BLOCKED"
        if trade.risk_amount <= 0: return False, "INVALID_RISK"
        if trade.entry == trade.stop: return False, "ZERO_STOP_DISTANCE"
        return True, "RISK_OK"

class FTMOGuardian:
    def __init__(self, config=None):
        self.config = config or FTMOConfig()
    def validate(self, trade):
        checks = []
        if trade.symbol not in self.config.allowed_symbols: checks.append("SYMBOL_NOT_ALLOWED")
        if trade.stop is None: checks.append("NO_STOP")
        if abs(trade.daily_pnl) + trade.risk_amount > self.config.max_daily_loss: checks.append("DAILY_LOSS_LIMIT_RISK")
        if abs(trade.total_pnl) + trade.risk_amount > self.config.max_total_loss: checks.append("TOTAL_LOSS_LIMIT_RISK")
        if trade.daily_trades >= self.config.max_daily_trades: checks.append("MAX_DAILY_TRADES")
        if not trade.session_allowed: checks.append("SESSION_NOT_ALLOWED")
        if trade.news_blocked and self.config.restricted_news_events: checks.append("RESTRICTED_NEWS_EVENT")
        if trade.loss_streak >= 3: checks.append("LOSS_STREAK_BLOCK")
        return (False, checks) if checks else (True, ["FTMO_RISK_OK"])

class ValidationProtocol:
    def validate_edge(self, report):
        required = ["in_sample","out_of_sample","walk_forward","monte_carlo","slippage","spread","stress","ruin_risk"]
        missing = [k for k in required if k not in report]
        if missing: return "ABORTAR_PROMOÇÃO", {"missing": missing}
        if not all(report.values()): return "ABORTAR_PROMOÇÃO", {"failed": [k for k,v in report.items() if not v]}
        return "P8.26_READY_FOR_PAPER_TRADING", {}

class DualModeEngine:
    def __init__(self, base="mind_trader"):
        self.research = Ledger(f"{base}/logs/RESEARCH_LEDGER.jsonl")
        self.ftmo = Ledger(f"{base}/logs/FTMO_SIMULATION_LEDGER.jsonl")
        self.risk = RiskGuardian()
        self.ftmo_guard = FTMOGuardian()
    def process_trade(self, trade):
        risk_ok, risk_reason = self.risk.validate(trade)
        ftmo_ok, ftmo_reason = self.ftmo_guard.validate(trade)
        event = asdict(trade) | {"risk_ok":risk_ok,"risk_reason":risk_reason,"ftmo_ok":ftmo_ok,"ftmo_reason":ftmo_reason,"decision":"OPERAR_SIMULADO" if risk_ok and ftmo_ok else "NAO_OPERAR"}
        return (self.research if trade.mode=="RESEARCH_MAX_RETURN_MODE" else self.ftmo).write(event)

def module_status():
    return {"P8.26":"APPROVED_FOR_RESEARCH_ONLY","P8.27":"FTMO_SIMULATION_ACTIVE","production":"BLOCKED","edge_claim":"NONE"}

