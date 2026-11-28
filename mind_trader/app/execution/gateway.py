import json, uuid, math
from app.runtime.p2343_post_loss_governance_gate import post_loss_gate
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.engines.core import RiskGuardian, FTMOGuardian, FTMOConfig, TradeIntent
from mind_trader.app.engines.regime_detection import require_defined_regime
from mind_trader.app.validation.adversarial_ai import AdversarialValidationEngine
from mind_trader.app.risk.ftmo_ruleset import load_ftmo_config, audit_rule_application
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.execution.paper_broker_adapter import paper_route_order
from mind_trader.app.security.institutional_live_lock import institutional_live_lock

ALLOWED_MODES={"PAPER","REPLAY","MICRO_SIM"}
LIVE_MODE_TO_ACTION={"LIVE":"LIVE_TRADE","PRODUCTION":"PRODUCTION_TRADE","REAL_MONEY":"REAL_MONEY_TRADE","FTMO_REAL":"FTMO_REAL_TRADE","BROKER":"BROKER_SEND_ORDER"}

def write_execution_ledger(event,path="mind_trader/logs/P8.41_EXECUTION_LEDGER.jsonl"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    event["execution_id"]=str(uuid.uuid4())
    event["ts"]=datetime.now(UTC).isoformat()
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(event,ensure_ascii=False)+"\n")
    return event

def ftmo_config_from_ruleset(config):
    return FTMOConfig(account_size=config["account_size"],profit_target=config["profit_target"],max_daily_loss=config["max_daily_loss"],max_total_loss=config["max_total_loss"],max_daily_trades=config["max_daily_trades"],allowed_symbols=tuple(config["allowed_symbols"]),restricted_symbols=tuple(config["restricted_symbols"]),restricted_news_events=config["restricted_news_events"])

class ExecutionGateway:
    def __init__(self, ledger_path="mind_trader/logs/P8.41_EXECUTION_LEDGER.jsonl", ftmo_config_path="mind_trader/config/ftmo_ruleset.json", paper_session_path="mind_trader/logs/P8.48_PAPER_SESSION.json", paper_day_ledger_path="mind_trader/logs/P8.48_PAPER_DAY_LEDGER.jsonl", paper_broker_ledger_path="mind_trader/logs/P8.95_PAPER_BROKER_LEDGER.jsonl", trusted_context_provider=None):
        self.trusted_context_provider=trusted_context_provider
        self.risk=RiskGuardian()
        cfg,val=load_ftmo_config(ftmo_config_path)
        self.ftmo_config_valid=val
        self.ftmo_ruleset=cfg
        self.ftmo=FTMOGuardian(ftmo_config_from_ruleset(cfg)) if cfg and val["valid"] else None
        self.adv=AdversarialValidationEngine()
        self.ledger_path=ledger_path
        self.paper=PaperTradingSessionManager(paper_session_path,paper_day_ledger_path,ftmo_config_path)
        self.paper_broker_ledger_path=paper_broker_ledger_path

    def _post_loss_check(self, mode, trade_dict, session_check):
        try:
            if mode != "PAPER":
                raise ValueError("MODE_HISTORY_NOT_BOUND")
            state = self.paper.daily_summary()
            streak = state["loss_streak"]
            if (state["status"] != "OPEN" or not session_check["allowed"]
                or state["session_id"] != session_check["session_id"]
                or type(streak) is not int or streak < 0):
                raise ValueError("INVALID_SESSION_STATE")
            rows = [json.loads(line) for line in self.paper.ledger_path.read_text(encoding="utf-8").splitlines()]
            events = [row for row in rows if row.get("session_id") == state["session_id"]]
            if not events or events[0].get("type") != "SESSION_OPENED":
                raise ValueError("MISSING_SESSION_OPEN")
            if any(row.get("type") != "TRADE_RESULT" for row in events[1:]):
                raise ValueError("INVALID_SESSION_SEQUENCE")
            ids = [row["event_id"] for row in events]
            if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
                raise ValueError("INVALID_EVENT_ID")
            pnl, ledger_streak = 0.0, 0
            for index, row in enumerate(events[1:], 1):
                value = row["pnl"]
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise ValueError("INVALID_LEDGER_PNL")
                pnl += value
                ledger_streak = ledger_streak + 1 if value < 0 else 0
                if row["trades"] != index or row["daily_pnl"] != pnl:
                    raise ValueError("LEDGER_SEQUENCE_MISMATCH")
            if (state["trades"] != len(events)-1 or state["daily_pnl"] != pnl
                or streak != ledger_streak or self.paper.daily_summary() != state):
                raise ValueError("SESSION_LEDGER_MISMATCH")
            symbol, side = trade_dict["symbol"], trade_dict["side"]
            if not isinstance(symbol, str) or not symbol or side not in {"BUY", "SELL"}:
                raise ValueError("INVALID_ORDER_IDENTITY")
            context = {}
            evidence = None
            if streak:
                if self.trusted_context_provider is None:
                    raise ValueError("NO_TRUSTED_CONTEXT_PROVIDER")
                snapshot = self.trusted_context_provider(symbol, side, state["session_id"])
                if (snapshot["symbol"], snapshot["side"], snapshot["session_id"]) != (symbol, side, state["session_id"]):
                    raise ValueError("CONTEXT_IDENTITY_MISMATCH")
                evidence = snapshot["evidence_id"]
                if not isinstance(evidence, str) or not evidence.strip():
                    raise ValueError("MISSING_CONTEXT_EVIDENCE")
                observed = datetime.fromisoformat(snapshot["observed_at"])
                age = (datetime.now(UTC) - observed).total_seconds()
                if not 0 <= age <= 60:
                    raise ValueError("STALE_CONTEXT")
                keys = ("m1","m5","m15","h1","trend_filter","volatility_filter","session_filter","support_resistance_filter")
                context = {k: snapshot["context"][k] for k in keys}
                if any(type(v) is not bool for v in context.values()):
                    raise ValueError("INVALID_CONTEXT_FLAGS")
            result = post_loss_gate(symbol, side, streak > 0, context)
            return {"layer":"POST_LOSS","ok":result["status"] == "APPROVED",
                    "reason":result["reason"],"session_id":state["session_id"],
                    "loss_streak":streak,"ledger_event_id":ids[-1],"context_evidence_id":evidence}
        except Exception as exc:
            return {"layer":"POST_LOSS","ok":False,"reason":"POST_LOSS_PROVENANCE_BLOCK",
                    "error_type":type(exc).__name__}

    def submit_order(self, mode, trade_dict, regime_report, genome):
        if mode in LIVE_MODE_TO_ACTION:
            lock=institutional_live_lock(LIVE_MODE_TO_ACTION[mode],{"mode":mode,"trade":trade_dict})
            return write_execution_ledger({"mode":mode,"decision":lock["decision"],"live_lock":lock,"production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        if mode not in ALLOWED_MODES:
            return write_execution_ledger({"mode":mode,"decision":"BLOCKED_UNKNOWN_EXECUTION_MODE","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        if not self.ftmo or not self.ftmo_config_valid.get("valid"):
            return write_execution_ledger({"mode":mode,"decision":"BLOCKED_INVALID_FTMO_CONFIG","ftmo_config_validation":self.ftmo_config_valid,"production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        session_check=self.paper.pre_trade_check(trade_dict.get("risk_amount",0))
        if mode=="PAPER" and not session_check["allowed"]:
            return write_execution_ledger({"mode":mode,"decision":"BLOCKED_PAPER_SESSION","session_check":session_check,"production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        post_loss=self._post_loss_check(mode, trade_dict, session_check)
        if not post_loss["ok"]:
            return write_execution_ledger({"mode":mode,"decision":"REJECT_ORDER","checks":[post_loss],"production":"BLOCKED","real_broker_routing":"DISABLED","edge_claim":"NONE"},self.ledger_path)
        trade_dict=dict(trade_dict, loss_streak=post_loss["loss_streak"])
        trade=TradeIntent(mode="FTMO_EVALUATION_SIMULATION_MODE",symbol=trade_dict["symbol"],strategy_id=trade_dict["strategy_id"],regime=regime_report.get("regime","UNDEFINED"),entry=trade_dict["entry"],stop=trade_dict.get("stop"),target=trade_dict["target"],risk_amount=trade_dict["risk_amount"],open_risk=trade_dict.get("open_risk",0),daily_pnl=trade_dict.get("daily_pnl",0),total_pnl=trade_dict.get("total_pnl",0),daily_trades=trade_dict.get("daily_trades",0),loss_streak=trade_dict.get("loss_streak",0),session_allowed=trade_dict.get("session_allowed",True),news_blocked=trade_dict.get("news_blocked",False))

        rule_audit=audit_rule_application(trade_dict,self.ftmo_ruleset)
        checks=[post_loss]
        ok,reason=self.risk.validate(trade); checks.append({"layer":"RISK","ok":ok,"reason":reason})
        fok,freason=self.ftmo.validate(trade); checks.append({"layer":"FTMO_RULESET","ok":fok and rule_audit["decision"]=="ALLOW_FTMO_SIMULATION","reason":freason,"config_hash":self.ftmo_config_valid.get("hash")})
        rok,rreason=require_defined_regime(regime_report); checks.append({"layer":"REGIME","ok":rok,"reason":rreason})
        adv=self.adv.review_trade(trade_dict,regime_report,genome); checks.append({"layer":"ADVERSARIAL","ok":adv["adversarial_passed"],"reason":adv["decision"]})
        checks.append({"layer":"PAPER_SESSION","ok":session_check["allowed"] if mode=="PAPER" else True,"reason":session_check["decision"]})

        allowed=all(c["ok"] for c in checks)
        paper_broker=None
        if allowed and mode=="PAPER":
            paper_order={"symbol":trade.symbol,"side":trade_dict.get("side","BUY"),"entry":trade.entry,"stop":trade.stop,"target":trade.target,"risk_amount":trade.risk_amount,"strategy_id":trade.strategy_id}
            paper_broker=paper_route_order(paper_order,ledger_path=self.paper_broker_ledger_path,ftmo_config_path=self.paper.ftmo_config_path)

        return write_execution_ledger({"mode":mode,"symbol":trade.symbol,"strategy_id":trade.strategy_id,"genome_id":genome.get("genome_id"),"regime":regime_report.get("regime"),"ftmo_config_version":self.ftmo_ruleset.get("version"),"ftmo_config_hash":self.ftmo_config_valid.get("hash"),"checks":checks,"paper_broker":paper_broker,"decision":"ACCEPT_SIMULATED_ORDER" if allowed else "REJECT_ORDER","order_status":"SIMULATED_ACCEPTED" if allowed else "SIMULATED_REJECTED","production":"BLOCKED","real_broker_routing":"DISABLED","edge_claim":"NONE"},self.ledger_path)

def broker_contracts():
    return {"MT5":{"status":"CONTRACT_PLACEHOLDER_DISABLED_FOR_REAL_EXECUTION","allowed_modes":["PAPER","REPLAY","MICRO_SIM"]},"PROFIT":{"status":"CONTRACT_PLACEHOLDER_DISABLED_FOR_REAL_EXECUTION","allowed_modes":["PAPER","REPLAY","MICRO_SIM"]},"production":"BLOCKED"}

