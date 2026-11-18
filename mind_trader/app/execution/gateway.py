import json, uuid, math
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
    def __init__(self, ledger_path="mind_trader/logs/P8.41_EXECUTION_LEDGER.jsonl", ftmo_config_path="mind_trader/config/ftmo_ruleset.json", paper_session_path="mind_trader/logs/P8.48_PAPER_SESSION.json", paper_day_ledger_path="mind_trader/logs/P8.48_PAPER_DAY_LEDGER.jsonl", paper_broker_ledger_path="mind_trader/logs/P8.95_PAPER_BROKER_LEDGER.jsonl"):
        self.risk=RiskGuardian()
        cfg,val=load_ftmo_config(ftmo_config_path)
        self.ftmo_config_valid=val
        self.ftmo_ruleset=cfg
        self.ftmo=FTMOGuardian(ftmo_config_from_ruleset(cfg)) if cfg and val["valid"] else None
        self.adv=AdversarialValidationEngine(cfg["max_daily_loss"],cfg["max_total_loss"]) if self.ftmo else None
        self.ledger_path=ledger_path
        self.paper=PaperTradingSessionManager(paper_session_path,paper_day_ledger_path,ftmo_config_path)
        self.paper_broker_ledger_path=paper_broker_ledger_path

    def submit_order(self, mode, trade_dict, regime_report, genome):
        if not isinstance(mode,str):
            return write_execution_ledger({"decision":"BLOCKED_UNKNOWN_EXECUTION_MODE","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)
        if mode in LIVE_MODE_TO_ACTION:
            lock=institutional_live_lock(LIVE_MODE_TO_ACTION[mode],{"mode":mode,"trade":trade_dict})
            return write_execution_ledger({"mode":mode,"decision":lock["decision"],"live_lock":lock,"production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        if mode not in ALLOWED_MODES:
            return write_execution_ledger({"mode":mode,"decision":"BLOCKED_UNKNOWN_EXECUTION_MODE","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        if not self.ftmo or not self.ftmo_config_valid.get("valid"):
            return write_execution_ledger({"mode":mode,"decision":"BLOCKED_INVALID_FTMO_CONFIG","ftmo_config_validation":self.ftmo_config_valid,"production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        # Reject malformed inputs before session arithmetic or downstream routing.
        if not isinstance(trade_dict, dict) or not isinstance(regime_report, dict) or not isinstance(genome, dict):
            return write_execution_ledger({"mode":mode,"decision":"REJECT_ORDER","reason":"INVALID_INPUT","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)
        if any(type(trade_dict.get(k, default)) is not bool for k, default in (("session_allowed",True),("news_blocked",False))):
            return write_execution_ledger({"mode":mode,"decision":"REJECT_ORDER","reason":"INVALID_POLICY_FLAG","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)
        for k in ("symbol","strategy_id"):
            if not isinstance(trade_dict.get(k),str) or not trade_dict[k].strip():
                return write_execution_ledger({"mode":mode,"decision":"REJECT_ORDER","reason":"INVALID_IDENTITY","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)
        for k in ("entry","target","risk_amount","stop","open_risk","daily_pnl","total_pnl"):
            v=trade_dict.get(k,0 if k in ("open_risk","daily_pnl","total_pnl") else None)
            if k=="stop" and v is None: continue
            if type(v) not in (int,float) or not math.isfinite(v):
                return write_execution_ledger({"mode":mode,"decision":"REJECT_ORDER","reason":"INVALID_NUMERIC_INPUT","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)
        if any(type(trade_dict.get(k,0)) is not int or trade_dict.get(k,0)<0 for k in ("daily_trades","loss_streak")):
            return write_execution_ledger({"mode":mode,"decision":"REJECT_ORDER","reason":"INVALID_COUNTER","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)
        if mode=="PAPER" and (not isinstance(trade_dict.get("side","BUY"),str) or trade_dict.get("side","BUY").upper() not in ("BUY","SELL")):
            return write_execution_ledger({"mode":mode,"decision":"REJECT_ORDER","reason":"INVALID_SIDE","production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        session_check=self.paper.pre_trade_check(trade_dict.get("risk_amount",0))
        if mode=="PAPER" and not session_check["allowed"]:
            return write_execution_ledger({"mode":mode,"decision":"BLOCKED_PAPER_SESSION","session_check":session_check,"production":"BLOCKED","edge_claim":"NONE"},self.ledger_path)

        trade=TradeIntent(mode="FTMO_EVALUATION_SIMULATION_MODE",symbol=trade_dict["symbol"],strategy_id=trade_dict["strategy_id"],regime=regime_report.get("regime","UNDEFINED"),entry=trade_dict["entry"],stop=trade_dict.get("stop"),target=trade_dict["target"],risk_amount=trade_dict["risk_amount"],open_risk=trade_dict.get("open_risk",0),daily_pnl=trade_dict.get("daily_pnl",0),total_pnl=trade_dict.get("total_pnl",0),daily_trades=trade_dict.get("daily_trades",0),loss_streak=trade_dict.get("loss_streak",0),session_allowed=trade_dict.get("session_allowed",True),news_blocked=trade_dict.get("news_blocked",False))

        rule_audit=audit_rule_application(trade_dict,self.ftmo_ruleset)
        checks=[]
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

        if allowed and mode=="PAPER":
            allowed=isinstance(paper_broker,dict) and paper_broker.get("decision")=="PAPER_ORDER_ACCEPTED" and paper_broker.get("order_status")=="PAPER_FILLED_SIMULATED"
        return write_execution_ledger({"mode":mode,"symbol":trade.symbol,"strategy_id":trade.strategy_id,"genome_id":genome.get("genome_id"),"regime":regime_report.get("regime"),"ftmo_config_version":self.ftmo_ruleset.get("version"),"ftmo_config_hash":self.ftmo_config_valid.get("hash"),"checks":checks,"paper_broker":paper_broker,"decision":"ACCEPT_SIMULATED_ORDER" if allowed else "REJECT_ORDER","order_status":"SIMULATED_ACCEPTED" if allowed else "SIMULATED_REJECTED","production":"BLOCKED","real_broker_routing":"DISABLED","edge_claim":"NONE"},self.ledger_path)

def broker_contracts():
    return {"MT5":{"status":"CONTRACT_PLACEHOLDER_DISABLED_FOR_REAL_EXECUTION","allowed_modes":["PAPER","REPLAY","MICRO_SIM"]},"PROFIT":{"status":"CONTRACT_PLACEHOLDER_DISABLED_FOR_REAL_EXECUTION","allowed_modes":["PAPER","REPLAY","MICRO_SIM"]},"production":"BLOCKED"}

