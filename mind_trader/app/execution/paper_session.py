import json, uuid, math, os, tempfile
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
        fd, temporary = tempfile.mkstemp(prefix=".paper_session_", dir=str(self.session_path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(s, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.session_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return s

    def _read_session(self):
        if not self.session_path.exists(): return None
        try:
            session = json.loads(self.session_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            return None
        if not isinstance(session, dict):
            return None
        required = ("session_id", "status", "trades", "max_daily_trades", "daily_pnl",
                    "max_daily_loss", "loss_streak", "ftmo_config_hash")
        if any(key not in session for key in required):
            return None
        for key in ("trades", "max_daily_trades", "loss_streak"):
            if type(session[key]) is not int or session[key] < 0:
                return None
        for key in ("daily_pnl", "max_daily_loss"):
            value = session[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                return None
        if session["max_daily_trades"] <= 0 or session["max_daily_loss"] <= 0:
            return None
        if session["trades"] > session["max_daily_trades"]:
            return None
        pending = session.get("pending_paper_orders", [])
        if not isinstance(pending, list):
            return None
        if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) or not x["id"]
               or isinstance(x.get("risk"), bool) or not isinstance(x.get("risk"), (int, float))
               or not math.isfinite(x["risk"]) or x["risk"] <= 0 for x in pending):
            return None
        if len({x["id"] for x in pending}) != len(pending):
            return None
        if session["trades"] + len(pending) > session["max_daily_trades"]:
            return None
        if not isinstance(session["session_id"], str) or not session["session_id"]:
            return None
        if session["status"] not in ("OPEN", "CLOSED"):
            return None
        if not isinstance(session["ftmo_config_hash"], str):
            return None
        return session

    def _ledger(self, event):
        self.ledger_path.parent.mkdir(parents=True,exist_ok=True)
        event["event_id"]=str(uuid.uuid4())
        event["ts"]=_now()
        with open(self.ledger_path,"a",encoding="utf-8") as f:
            f.write(json.dumps(event,ensure_ascii=False)+"\n")
        return event

    def open_session(self, account_id="PAPER_FTMO_SIM"):
        # Protect creation/reopening against concurrent reservations and closes.
        lock_path = self.session_path.with_name(self.session_path.name + ".reserve.lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return {"decision":"BLOCK_OPEN_RESERVATION_LOCKED","production":"BLOCKED"}
        try:
            os.close(fd)
            cfg,val=load_ftmo_config(self.ftmo_config_path)
            if not cfg or not val["valid"]:
                return {"decision":"BLOCK_SESSION_INVALID_FTMO_CONFIG","validation":val,"production":"BLOCKED"}
            existing=self._read_session()
            if self.session_path.exists() and existing is None:
                return {"decision":"BLOCK_CORRUPT_PAPER_SESSION","production":"BLOCKED"}
            if existing and existing.get("pending_paper_orders"):
                return {"decision":"BLOCK_SESSION_PENDING_RESERVATIONS","production":"BLOCKED"}
            if existing and existing.get("status")=="OPEN":
                return {"decision":"SESSION_ALREADY_OPEN","session":existing,"production":"BLOCKED"}
            if existing and existing.get("status")=="CLOSED" and (not isinstance(existing.get("opened_at"), str) or not existing["opened_at"]):
                return {"decision":"BLOCK_SESSION_MISSING_OPEN_TIMESTAMP","production":"BLOCKED"}
            if existing and existing.get("status")=="CLOSED":
                try:
                    opened = datetime.fromisoformat(existing["opened_at"])
                    if opened.tzinfo is None or opened.utcoffset() is None:
                        raise ValueError("opening timestamp must be timezone-aware")
                    opened_day = opened.astimezone(UTC).date()
                except (ValueError, TypeError, OverflowError):
                    return {"decision":"BLOCK_SESSION_INVALID_OPEN_TIMESTAMP","production":"BLOCKED"}
                try:
                    closed = datetime.fromisoformat(existing["closed_at"])
                    if closed.tzinfo is None or closed.utcoffset() is None:
                        raise ValueError("closing timestamp must be timezone-aware")
                    closed_utc = closed.astimezone(UTC)
                except (KeyError, ValueError, TypeError, OverflowError):
                    return {"decision":"BLOCK_SESSION_INVALID_CLOSE_TIMESTAMP","production":"BLOCKED"}
                if closed_utc < opened.astimezone(UTC):
                    return {"decision":"BLOCK_SESSION_INVALID_CLOSE_TIMESTAMP","production":"BLOCKED"}
                if closed_utc > datetime.now(UTC):
                    return {"decision":"BLOCK_SESSION_FUTURE_CLOSE_TIMESTAMP","production":"BLOCKED"}
                if opened_day >= datetime.now(UTC).date() or closed_utc.date() >= datetime.now(UTC).date():
                    return {"decision":"BLOCK_SAME_DAY_SESSION_RESET","production":"BLOCKED"}
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
    
        finally:
            try:
                lock_path.unlink()
            except OSError:
                pass

    def close_session(self, reason="MANUAL_CLOSE"):
        # Serialize lifecycle transitions with PAPER reservation and settlement.
        lock_path = self.session_path.with_name(self.session_path.name + ".reserve.lock")
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return {"decision":"BLOCK_CLOSE_RESERVATION_LOCKED","production":"BLOCKED"}
        try:
            os.close(fd)
            s = self._read_session()
            if not s or s.get("status") != "OPEN":
                return {"decision":"NO_OPEN_SESSION","production":"BLOCKED"}
            if s.get("pending_paper_orders"):
                return {"decision":"BLOCK_CLOSE_PENDING_RESERVATIONS","production":"BLOCKED"}
            s["status"] = "CLOSED"
            s["closed_at"] = _now()
            s["close_reason"] = reason
            self._write_session(s)
            self._ledger({"type":"SESSION_CLOSED","session_id":s["session_id"],"reason":reason,"daily_pnl":s["daily_pnl"],"trades":s["trades"]})
            return {"decision":"SESSION_CLOSED","session":s,"production":"BLOCKED"}
        except (OSError, ValueError, TypeError, KeyError):
            return {"decision":"BLOCK_CLOSE_SESSION_ERROR","production":"BLOCKED"}
        finally:
            try:
                lock_path.unlink()
            except OSError:
                pass

    def pre_trade_check(self, risk_amount):
        if isinstance(risk_amount, bool) or not isinstance(risk_amount, (int, float)) or not math.isfinite(risk_amount) or risk_amount <= 0:
            return {"allowed":False,"decision":"BLOCK_INVALID_RISK_AMOUNT","production":"BLOCKED"}
        s=self._read_session()
        if not s: return {"allowed":False,"decision":"BLOCK_NO_SESSION","production":"BLOCKED"}
        if s.get("status")!="OPEN": return {"allowed":False,"decision":"BLOCK_SESSION_CLOSED","production":"BLOCKED"}
        try:
            opened = datetime.fromisoformat(s["opened_at"])
            if opened.tzinfo is None or opened.utcoffset() is None:
                raise ValueError("timezone required")
            if opened.astimezone(UTC).date() != datetime.now(UTC).date():
                return {"allowed":False,"decision":"BLOCK_PAPER_SESSION_DAY_MISMATCH","production":"BLOCKED"}
        except (KeyError, ValueError, TypeError, OverflowError):
            return {"allowed":False,"decision":"BLOCK_PAPER_SESSION_INVALID_OPEN_TIMESTAMP","production":"BLOCKED"}
        cfg, validation = load_ftmo_config(self.ftmo_config_path)
        if not cfg or not validation.get("valid") or validation.get("hash") != s["ftmo_config_hash"]:
            return {"allowed":False,"decision":"BLOCK_PAPER_SESSION_FTMO_CONFIG_DRIFT","production":"BLOCKED"}
        if s["max_daily_trades"] != cfg["max_daily_trades"] or s["max_daily_loss"] != cfg["max_daily_loss"]:
            return {"allowed":False,"decision":"BLOCK_PAPER_SESSION_LIMIT_TAMPERING","production":"BLOCKED"}
        pending = s.get("pending_paper_orders", [])
        if not isinstance(pending, list) or any(not isinstance(x, dict) or not isinstance(x.get("risk"), (int, float)) or isinstance(x.get("risk"), bool) or not math.isfinite(x["risk"]) or x["risk"] <= 0 or not isinstance(x.get("id"), str) for x in pending):
            return {"allowed":False,"decision":"BLOCK_PAPER_RESERVATION_CORRUPT","production":"BLOCKED"}
        if s["trades"] + len(pending) >= s["max_daily_trades"]: return {"allowed":False,"decision":"BLOCK_MAX_DAILY_TRADES","production":"BLOCKED"}
        if s["daily_pnl"] < -s["max_daily_loss"]:
            return {"allowed":False,"decision":"BLOCK_DAILY_LOSS_BREACHED","production":"BLOCKED"}
        # Only realized losses consume the daily loss allowance; profits do not.
        if max(0.0, -s["daily_pnl"]) + sum(x["risk"] for x in pending) + risk_amount > s["max_daily_loss"]:
            return {"allowed":False,"decision":"BLOCK_DAILY_LOSS_LIMIT","production":"BLOCKED"}
        return {"allowed":True,"decision":"ALLOW_PAPER_TRADE","session_id":s["session_id"],"production":"BLOCKED"}

    def reserve_paper_order(self, risk_amount, client_order_id=None):
        """Durable fail-closed reservation, serialized across processes via O_EXCL."""
        import os
        if not isinstance(client_order_id, str) or not client_order_id.strip() or len(client_order_id) > 128:
            return {"allowed":False,"decision":"BLOCK_MISSING_CLIENT_ORDER_ID","production":"BLOCKED"}
        lock_path = self.session_path.with_name(self.session_path.name + ".reserve.lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return {"allowed":False,"decision":"BLOCK_PAPER_RESERVATION_LOCKED","production":"BLOCKED"}
        try:
            os.close(fd)
            session_before = self._read_session()
            if not session_before or session_before.get("status") != "OPEN":
                return {"allowed":False,"decision":"BLOCK_NO_SESSION","production":"BLOCKED"}
            known = session_before.get("client_order_ids", [])
            if not isinstance(known, list) or any(not isinstance(x,str) for x in known):
                return {"allowed":False,"decision":"BLOCK_CORRUPT_ORDER_IDS","production":"BLOCKED"}
            if client_order_id in known:
                return {"allowed":False,"decision":"BLOCK_DUPLICATE_CLIENT_ORDER_ID","production":"BLOCKED"}
            checked = self.pre_trade_check(risk_amount)
            if not checked["allowed"]:
                return checked
            session = self._read_session()
            pending = session.get("pending_paper_orders", [])
            if not isinstance(pending, list) or any(not isinstance(x, dict) or not isinstance(x.get("risk"), (int, float)) or isinstance(x.get("risk"), bool) or not math.isfinite(x["risk"]) or x["risk"] <= 0 or not isinstance(x.get("id"), str) for x in pending):
                return {"allowed":False,"decision":"BLOCK_PAPER_RESERVATION_CORRUPT","production":"BLOCKED"}
            if session["trades"] + len(pending) >= session["max_daily_trades"]:
                return {"allowed":False,"decision":"BLOCK_MAX_DAILY_TRADES","production":"BLOCKED"}
            if max(0.0, -session["daily_pnl"]) + sum(x["risk"] for x in pending) + risk_amount > session["max_daily_loss"]:
                return {"allowed":False,"decision":"BLOCK_DAILY_LOSS_LIMIT","production":"BLOCKED"}
            token = str(uuid.uuid4())
            pending.append({"id":token,"risk":risk_amount,"client_order_id":client_order_id})
            session["client_order_ids"] = known + [client_order_id]
            session["pending_paper_orders"] = pending
            self._write_session(session)
            return {"allowed":True,"decision":"PAPER_ORDER_RESERVED","reservation_id":token,"production":"BLOCKED"}
        except (OSError, ValueError, TypeError, KeyError, OverflowError):
            return {"allowed":False,"decision":"BLOCK_PAPER_RESERVATION_ERROR","production":"BLOCKED"}
        finally:
            try:
                lock_path.unlink()
            except OSError:
                pass

    def release_paper_order(self, reservation_id):
        """Release only a rejected PAPER order; failures retain reservation (fail-closed)."""
        import os
        lock_path = self.session_path.with_name(self.session_path.name + ".reserve.lock")
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return False
        try:
            os.close(fd)
            session = self._read_session()
            if not session:
                return False
            pending = session.get("pending_paper_orders", [])
            if not isinstance(pending, list) or sum(x.get("id") == reservation_id for x in pending if isinstance(x, dict)) != 1:
                return False
            session["pending_paper_orders"] = [x for x in pending if x.get("id") != reservation_id]
            self._write_session(session)
            return True
        except (OSError, ValueError, TypeError, KeyError):
            return False
        finally:
            try:
                lock_path.unlink()
            except OSError:
                pass

    def record_trade_result(self, pnl):
        """Legacy result accounting serialized with PAPER reservations and settlement."""
        lock_path = self.session_path.with_name(self.session_path.name + ".reserve.lock")
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return {"decision":"BLOCK_RECORD_RESERVATION_LOCKED","production":"BLOCKED"}
        try:
            os.close(fd)
            if isinstance(pnl, bool) or not isinstance(pnl, (int, float)) or not math.isfinite(pnl):
                return {"decision":"BLOCK_RECORD_INVALID_PNL","production":"BLOCKED"}
            s=self._read_session()
            if not s or s.get("status")!="OPEN":
                return {"decision":"BLOCK_RECORD_NO_OPEN_SESSION","production":"BLOCKED"}
            cfg, validation = load_ftmo_config(self.ftmo_config_path)
            if not cfg or not validation.get("valid") or validation.get("hash") != s["ftmo_config_hash"]:
                return {"decision":"BLOCK_RECORD_FTMO_CONFIG_DRIFT","production":"BLOCKED"}
            if s["max_daily_trades"] != cfg["max_daily_trades"] or s["max_daily_loss"] != cfg["max_daily_loss"]:
                return {"decision":"BLOCK_RECORD_SESSION_LIMIT_TAMPERING","production":"BLOCKED"}
            next_daily_pnl = s["daily_pnl"] + pnl
            if not math.isfinite(next_daily_pnl):
                return {"decision":"BLOCK_RECORD_INVALID_PNL","production":"BLOCKED"}
            pending = s.get("pending_paper_orders", [])
            if pending:
                return {"decision":"BLOCK_RECORD_PENDING_RESERVATION_REQUIRES_SETTLEMENT_ID","production":"BLOCKED"}
            if s["trades"] >= s["max_daily_trades"]:
                return {"decision":"BLOCK_RECORD_TRADE_LIMIT","production":"BLOCKED"}
            s["trades"] += 1
            s["daily_pnl"] = next_daily_pnl
            s["loss_streak"] = s["loss_streak"] + 1 if pnl < 0 else 0
            self._write_session(s)
            self._ledger({"type":"TRADE_RESULT","session_id":s["session_id"],"pnl":pnl,"daily_pnl":s["daily_pnl"],"trades":s["trades"]})
            return {"decision":"TRADE_RECORDED","session":s,"production":"BLOCKED"}
        except (OSError, ValueError, TypeError, KeyError, OverflowError):
            return {"decision":"BLOCK_RECORD_SESSION_ERROR","production":"BLOCKED"}
        finally:
            try:
                lock_path.unlink()
            except OSError:
                pass

    def settle_paper_order(self, reservation_id, pnl):
        """Settle exactly one reserved PAPER fill under the interprocess lock."""
        import os
        if not isinstance(reservation_id, str) or not reservation_id or isinstance(pnl, bool) or not isinstance(pnl, (int, float)) or not math.isfinite(pnl):
            return {"decision":"BLOCK_SETTLEMENT_INVALID_INPUT","production":"BLOCKED"}
        lock_path = self.session_path.with_name(self.session_path.name + ".reserve.lock")
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError:
            return {"decision":"BLOCK_PAPER_RESERVATION_LOCKED","production":"BLOCKED"}
        try:
            os.close(fd)
            s = self._read_session()
            if not s or s.get("status") != "OPEN":
                return {"decision":"BLOCK_SETTLEMENT_NO_OPEN_SESSION","production":"BLOCKED"}
            cfg, validation = load_ftmo_config(self.ftmo_config_path)
            if not cfg or not validation.get("valid") or validation.get("hash") != s["ftmo_config_hash"]:
                return {"decision":"BLOCK_SETTLEMENT_CONFIG_DRIFT","production":"BLOCKED"}
            if s["max_daily_trades"] != cfg["max_daily_trades"] or s["max_daily_loss"] != cfg["max_daily_loss"]:
                return {"decision":"BLOCK_SETTLEMENT_LIMIT_TAMPERING","production":"BLOCKED"}
            pending = s.get("pending_paper_orders", [])
            if not isinstance(pending, list) or any(not isinstance(x, dict) or not isinstance(x.get("id"), str) or isinstance(x.get("risk"), bool) or not isinstance(x.get("risk"), (int, float)) or not math.isfinite(x["risk"]) or x["risk"] <= 0 for x in pending):
                return {"decision":"BLOCK_SETTLEMENT_CORRUPT_RESERVATIONS","production":"BLOCKED"}
            if sum(x["id"] == reservation_id for x in pending) != 1:
                return {"decision":"BLOCK_SETTLEMENT_UNKNOWN_OR_DUPLICATE_ID","production":"BLOCKED"}
            if s["trades"] >= s["max_daily_trades"]:
                return {"decision":"BLOCK_SETTLEMENT_TRADE_LIMIT","production":"BLOCKED"}
            next_pnl = s["daily_pnl"] + pnl
            if not math.isfinite(next_pnl):
                return {"decision":"BLOCK_SETTLEMENT_INVALID_PNL","production":"BLOCKED"}
            s["pending_paper_orders"] = [x for x in pending if x["id"] != reservation_id]
            s["trades"] += 1
            s["daily_pnl"] = next_pnl
            s["loss_streak"] = s["loss_streak"] + 1 if pnl < 0 else 0
            self._write_session(s)
            self._ledger({"type":"PAPER_RESERVATION_SETTLED","session_id":s["session_id"],"reservation_id":reservation_id,"pnl":pnl,"daily_pnl":next_pnl,"trades":s["trades"]})
            return {"decision":"PAPER_RESERVATION_SETTLED","session":s,"production":"BLOCKED"}
        except (OSError, ValueError, TypeError, KeyError, OverflowError):
            return {"decision":"BLOCK_SETTLEMENT_ERROR","production":"BLOCKED"}
        finally:
            try:
                lock_path.unlink()
            except OSError:
                pass

    def reconcile_paper_fills(self, broker_ledger_path):
        """Read-only reconciliation. Ambiguous fills block new PAPER orders."""
        try:
            session = self._read_session()
            if not session or session.get("status") != "OPEN":
                return {"decision":"BLOCK_RECONCILIATION_NO_SESSION","production":"BLOCKED"}
            pending = session.get("pending_paper_orders", [])
            if not isinstance(pending, list):
                return {"decision":"BLOCK_RECONCILIATION_CORRUPT_SESSION","production":"BLOCKED"}
            path = Path(broker_ledger_path)
            rows = []
            if path.exists():
                for line in path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        record = json.loads(line)
                        if not isinstance(record, dict):
                            raise ValueError("invalid broker record")
                        rows.append(record)
            accepted = [row for row in rows if row.get("decision") == "PAPER_ORDER_ACCEPTED"]
            counts = {}
            for row in accepted:
                order = row.get("order")
                if not isinstance(order, dict):
                    raise ValueError("accepted record without order")
                token = order.get("reservation_id")
                if not isinstance(token, str) or not token:
                    return {"decision":"BLOCK_UNCORRELATED_BROKER_FILL","production":"BLOCKED"}
                counts[token] = counts.get(token, 0) + 1
            if any(count > 1 for count in counts.values()):
                return {"decision":"BLOCK_DUPLICATE_BROKER_FILL","production":"BLOCKED"}
            pending_ids = {item["id"] for item in pending}
            if any(token in pending_ids for token in counts):
                return {"decision":"BLOCK_UNSETTLED_BROKER_FILL","production":"BLOCKED"}
            if pending:
                return {"decision":"BLOCK_PENDING_PAPER_RESERVATIONS","production":"BLOCKED"}
            return {"decision":"PAPER_RECONCILIATION_CLEAN","production":"BLOCKED"}
        except (OSError, ValueError, TypeError, KeyError, UnicodeError):
            return {"decision":"BLOCK_RECONCILIATION_LEDGER_ERROR","production":"BLOCKED"}

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
