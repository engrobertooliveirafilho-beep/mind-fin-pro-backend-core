import json, uuid
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.risk.ftmo_ruleset import load_ftmo_config

def _now(): return datetime.now(UTC).isoformat()

class PaperTradingSessionManager:
    def __init__(self, session_path="mind_trader/logs/P8.48_PAPER_SESSION.json", ledger_path="mind_trader/logs/P8.48_PAPER_DAY_LEDGER.jsonl", ftmo_config_path="mind_trader/config/ftmo_ruleset.json"):
        self.session_path=Path(session_path)
        self.ledger_path=Path(ledger_path)
        self.ftmo_config_path=ftmo_config_path

    def _write_session(self, s):
        self.session_path.parent.mkdir(parents=True,exist_ok=True)
        self.session_path.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8")
        return s

    def _read_session(self):
        if not self.session_path.exists(): return None
        return json.loads(self.session_path.read_text(encoding="utf-8"))

    def _ledger(self, event):
        self.ledger_path.parent.mkdir(parents=True,exist_ok=True)
        event["event_id"]=str(uuid.uuid4())
        event["ts"]=_now()
        with open(self.ledger_path,"a",encoding="utf-8") as f:
            f.write(json.dumps(event,ensure_ascii=False)+"\n")
        return event

    def open_session(self, account_id="PAPER_FTMO_SIM"):
        cfg,val=load_ftmo_config(self.ftmo_config_path)
        if not cfg or not val["valid"]:
            return {"decision":"BLOCK_SESSION_INVALID_FTMO_CONFIG","validation":val,"production":"BLOCKED"}
        existing=self._read_session()
        if existing and existing.get("status")=="OPEN":
            return {"decision":"SESSION_ALREADY_OPEN","session":existing,"production":"BLOCKED"}
        s={
            "session_id":str(uuid.uuid4()),
            "account_id":account_id,
            "status":"OPEN",
            "opened_at":_now(),
            "closed_at":None,
            "daily_pnl":0.0,
            "trades":0,
            "loss_streak":0,
            "max_daily_trades":cfg["max_daily_trades"],
            "max_daily_loss":cfg["max_daily_loss"],
            "profit_target":cfg["profit_target"],
            "ftmo_config_hash":val["hash"],
            "production":"BLOCKED",
            "edge_claim":"NONE"
        }
        self._write_session(s)
        self._ledger({"type":"SESSION_OPENED","session_id":s["session_id"],"ftmo_config_hash":val["hash"]})
        return {"decision":"SESSION_OPENED","session":s,"production":"BLOCKED"}

    def close_session(self, reason="MANUAL_CLOSE"):
        s=self._read_session()
        if not s or s.get("status")!="OPEN":
            return {"decision":"NO_OPEN_SESSION","production":"BLOCKED"}
        s["status"]="CLOSED"
        s["closed_at"]=_now()
        s["close_reason"]=reason
        self._write_session(s)
        self._ledger({"type":"SESSION_CLOSED","session_id":s["session_id"],"reason":reason,"daily_pnl":s["daily_pnl"],"trades":s["trades"]})
        return {"decision":"SESSION_CLOSED","session":s,"production":"BLOCKED"}

    def pre_trade_check(self, risk_amount):
        s=self._read_session()
        if not s: return {"allowed":False,"decision":"BLOCK_NO_SESSION","production":"BLOCKED"}
        if s.get("status")!="OPEN": return {"allowed":False,"decision":"BLOCK_SESSION_CLOSED","production":"BLOCKED"}
        if s["trades"] >= s["max_daily_trades"]: return {"allowed":False,"decision":"BLOCK_MAX_DAILY_TRADES","production":"BLOCKED"}
        if abs(s["daily_pnl"]) + risk_amount > s["max_daily_loss"]: return {"allowed":False,"decision":"BLOCK_DAILY_LOSS_LIMIT","production":"BLOCKED"}
        return {"allowed":True,"decision":"ALLOW_PAPER_TRADE","session_id":s["session_id"],"production":"BLOCKED"}

    def record_trade_result(self, pnl):
        s=self._read_session()
        if not s or s.get("status")!="OPEN":
            return {"decision":"BLOCK_RECORD_NO_OPEN_SESSION","production":"BLOCKED"}
        s["trades"] += 1
        s["daily_pnl"] += float(pnl)
        s["loss_streak"] = s["loss_streak"] + 1 if pnl < 0 else 0
        self._write_session(s)
        self._ledger({"type":"TRADE_RESULT","session_id":s["session_id"],"pnl":pnl,"daily_pnl":s["daily_pnl"],"trades":s["trades"]})
        return {"decision":"TRADE_RECORDED","session":s,"production":"BLOCKED"}

    def daily_summary(self):
        s=self._read_session()
        if not s:
            return {"decision":"NO_SESSION_SUMMARY","production":"BLOCKED"}
        return {
            "decision":"DAILY_SUMMARY",
            "session_id":s["session_id"],
            "status":s["status"],
            "daily_pnl":s["daily_pnl"],
            "trades":s["trades"],
            "loss_streak":s["loss_streak"],
            "ftmo_config_hash":s["ftmo_config_hash"],
            "production":"BLOCKED",
            "edge_claim":"NONE"
        }
