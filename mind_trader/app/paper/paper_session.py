"""P8.48 PAPER-only session manager, recovered from Drive and fail-closed hardened."""
import json
import uuid
import math
import os
import tempfile
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.risk.ftmo_ruleset import load_ftmo_config

def _now():
    return datetime.now(UTC).isoformat()

class PaperTradingSessionManager:
    def __init__(self, session_path="mind_trader/logs/P8.48_PAPER_SESSION.json",
                 ledger_path="mind_trader/logs/P8.48_PAPER_DAY_LEDGER.jsonl",
                 ftmo_config_path="mind_trader/config/ftmo_ruleset.json"):
        self.session_path = Path(session_path)
        self.ledger_path = Path(ledger_path)
        self.ftmo_config_path = ftmo_config_path

    def _write_session(self, s):
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(s, ensure_ascii=False, indent=2, allow_nan=False)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=self.session_path.parent, delete=False) as tmp:
            tmp.write(payload)
            tmp_path = tmp.name
        os.replace(tmp_path, self.session_path)
        return s

    def _read_session(self):
        if not self.session_path.exists():
            return None
        try:
            data = json.loads(self.session_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return {"status":"CORRUPT"}
        return data if isinstance(data,dict) else {"status":"CORRUPT"}

    def _ledger(self, event):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        event["event_id"] = str(uuid.uuid4())
        event["ts"] = _now()
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")
        return event

    def _ledger_consistent(self, session):
        """Fail closed when the latest ledger event and session snapshot disagree."""
        try:
            lines = self.ledger_path.read_text(encoding="utf-8").splitlines()
            if not lines:
                return False
            events = [json.loads(line) for line in lines]
            related = [e for e in events if isinstance(e,dict) and e.get("session_id") == session.get("session_id")]
            if not related or related[0].get("type") != "SESSION_OPENED":
                return False
            last = related[-1]
            if last.get("type") == "SESSION_OPENED":
                return session.get("status") == "OPEN" and session.get("trades") == 0 and session.get("daily_pnl") == 0
            if last.get("type") == "TRADE_RESULT":
                return session.get("status") == "OPEN" and last.get("trades") == session.get("trades") and last.get("daily_pnl") == session.get("daily_pnl")
            if last.get("type") == "SESSION_CLOSED":
                return session.get("status") == "CLOSED" and last.get("trades") == session.get("trades") and last.get("daily_pnl") == session.get("daily_pnl")
            return False
        except (OSError, UnicodeError, ValueError, TypeError):
            return False

    def open_session(self, account_id="PAPER_FTMO_SIM"):
        cfg, val = load_ftmo_config(self.ftmo_config_path)
        if not cfg or not val["valid"]:
            return {"decision":"BLOCK_SESSION_INVALID_FTMO_CONFIG","validation":val,"production":"BLOCKED"}
        existing = self._read_session()
        if existing and existing.get("status") == "CLOSED" and not self._ledger_consistent(existing):
            return {"decision":"BLOCK_LEDGER_MISMATCH","production":"BLOCKED"}
        if existing and existing.get("status") != "CLOSED":
            return {"decision":"SESSION_ALREADY_OPEN" if existing.get("status") == "OPEN" else "BLOCK_INVALID_SESSION_STATE",
                    "session":existing,"production":"BLOCKED"}
        s = {"session_id":str(uuid.uuid4()),"account_id":account_id,"status":"OPEN",
             "opened_at":_now(),"closed_at":None,"daily_pnl":0.0,"trades":0,
             "loss_streak":0,"max_daily_trades":cfg["max_daily_trades"],
             "max_daily_loss":cfg["max_daily_loss"],"profit_target":cfg["profit_target"],
             "ftmo_config_hash":val["hash"],"production":"BLOCKED","edge_claim":"NONE"}
        self._write_session(s)
        self._ledger({"type":"SESSION_OPENED","session_id":s["session_id"],
                      "ftmo_config_hash":val["hash"]})
        return {"decision":"SESSION_OPENED","session":s,"production":"BLOCKED"}

    def close_session(self, reason="MANUAL_CLOSE"):
        s = self._read_session()
        if not s or s.get("status") != "OPEN":
            return {"decision":"NO_OPEN_SESSION","production":"BLOCKED"}
        if not self._ledger_consistent(s):
            return {"decision":"BLOCK_LEDGER_MISMATCH","production":"BLOCKED"}
        s["status"] = "CLOSED"
        s["closed_at"] = _now()
        s["close_reason"] = reason
        self._write_session(s)
        self._ledger({"type":"SESSION_CLOSED","session_id":s["session_id"],
                      "reason":reason,"daily_pnl":s["daily_pnl"],"trades":s["trades"]})
        return {"decision":"SESSION_CLOSED","session":s,"production":"BLOCKED"}

    def pre_trade_check(self, risk_amount):
        s = self._read_session()
        if not s:
            return {"allowed":False,"decision":"BLOCK_NO_SESSION","production":"BLOCKED"}
        if s.get("status") != "OPEN":
            return {"allowed":False,"decision":"BLOCK_SESSION_CLOSED","production":"BLOCKED"}
        if not self._ledger_consistent(s):
            return {"allowed":False,"decision":"BLOCK_LEDGER_MISMATCH","production":"BLOCKED"}
        cfg, validation = load_ftmo_config(self.ftmo_config_path)
        if not cfg or not validation["valid"] or validation["hash"] != s.get("ftmo_config_hash"):
            return {"allowed":False,"decision":"BLOCK_FTMO_CONFIG_CHANGED","production":"BLOCKED"}
        if (type(s.get("trades")) is not int or s["trades"] < 0
            or type(s.get("max_daily_trades")) is not int
            or s["max_daily_trades"] != cfg["max_daily_trades"]
            or type(s.get("max_daily_loss")) not in (int,float)
            or not math.isfinite(s["max_daily_loss"])
            or s["max_daily_loss"] != cfg["max_daily_loss"]):
            return {"allowed":False,"decision":"BLOCK_INVALID_SESSION_STATE","production":"BLOCKED"}
        if type(risk_amount) not in (int,float) or not math.isfinite(risk_amount) or risk_amount <= 0:
            return {"allowed":False,"decision":"BLOCK_INVALID_RISK","production":"BLOCKED"}
        if type(s.get("daily_pnl")) not in (int,float) or not math.isfinite(s["daily_pnl"]):
            return {"allowed":False,"decision":"BLOCK_INVALID_SESSION_PNL","production":"BLOCKED"}
        if s["trades"] >= s["max_daily_trades"]:
            return {"allowed":False,"decision":"BLOCK_MAX_DAILY_TRADES","production":"BLOCKED"}
        if max(0,-s["daily_pnl"]) + risk_amount > s["max_daily_loss"]:
            return {"allowed":False,"decision":"BLOCK_DAILY_LOSS_LIMIT","production":"BLOCKED"}
        return {"allowed":True,"decision":"ALLOW_PAPER_TRADE",
                "session_id":s["session_id"],"production":"BLOCKED"}

    def record_trade_result(self, pnl):
        s = self._read_session()
        if not s or s.get("status") != "OPEN":
            return {"decision":"BLOCK_RECORD_NO_OPEN_SESSION","production":"BLOCKED"}
        if not self._ledger_consistent(s):
            return {"decision":"BLOCK_LEDGER_MISMATCH","production":"BLOCKED"}
        cfg, validation = load_ftmo_config(self.ftmo_config_path)
        if not cfg or not validation["valid"] or validation["hash"] != s.get("ftmo_config_hash"):
            return {"decision":"BLOCK_FTMO_CONFIG_CHANGED","production":"BLOCKED"}
        if (type(s.get("trades")) is not int or s["trades"] < 0
            or type(s.get("max_daily_trades")) is not int
            or s["max_daily_trades"] != cfg["max_daily_trades"]
            or type(s.get("max_daily_loss")) not in (int,float)
            or not math.isfinite(s["max_daily_loss"])
            or s["max_daily_loss"] != cfg["max_daily_loss"]):
            return {"decision":"BLOCK_INVALID_SESSION_STATE","production":"BLOCKED"}
        if type(pnl) not in (int,float) or not math.isfinite(pnl):
            return {"decision":"BLOCK_INVALID_PNL","production":"BLOCKED"}
        if type(s.get("daily_pnl")) not in (int,float) or not math.isfinite(s["daily_pnl"]):
            return {"decision":"BLOCK_INVALID_SESSION_PNL","production":"BLOCKED"}
        next_daily_pnl = s["daily_pnl"] + float(pnl)
        if not math.isfinite(next_daily_pnl):
            return {"decision":"BLOCK_PNL_OVERFLOW","production":"BLOCKED"}
        s["trades"] += 1
        s["daily_pnl"] = next_daily_pnl
        s["loss_streak"] = s["loss_streak"] + 1 if pnl < 0 else 0
        self._write_session(s)
        self._ledger({"type":"TRADE_RESULT","session_id":s["session_id"],
                      "pnl":pnl,"daily_pnl":s["daily_pnl"],"trades":s["trades"]})
        return {"decision":"TRADE_RECORDED","session":s,"production":"BLOCKED"}

    def daily_summary(self):
        s = self._read_session()
        if not s:
            return {"decision":"NO_SESSION_SUMMARY","production":"BLOCKED"}
        return {"decision":"DAILY_SUMMARY","session_id":s["session_id"],
                "status":s["status"],"daily_pnl":s["daily_pnl"],"trades":s["trades"],
                "loss_streak":s["loss_streak"],"ftmo_config_hash":s["ftmo_config_hash"],
                "production":"BLOCKED","edge_claim":"NONE"}
