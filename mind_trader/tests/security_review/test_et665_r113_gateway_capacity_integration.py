"""ET665.R113: isolated original gateway method with session-aware capacity.

Run source via AST extraction and inject the PAPER-only broker gate. No MT5,
production imports, or real broker operations are executed.
"""
import ast
import json
from datetime import datetime, UTC
from pathlib import Path
import math
import runpy
from types import SimpleNamespace
import tempfile
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[3]
GATEWAY=ROOT/"products/eldora_trader/mind_trader/app/execution/gateway.py"
BROKER=ROOT/"mind_trader/app/execution/paper_broker_adapter.py"
EXEC=ROOT/"mind_trader/app/execution"
Gate=runpy.run_path(str(Path(__file__).with_name("et665_r113_paper_capacity_gate.py")))["PaperCapacityGate"]

def extract(path,name,ns,klass=None):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    nodes=tree.body if klass is None else next(n.body for n in tree.body if isinstance(n,ast.ClassDef) and n.name==klass)
    fn=next(n for n in nodes if isinstance(n,ast.FunctionDef) and n.name==name)
    selected=[fn] if klass is None else [ast.ClassDef(name=klass,bases=[],keywords=[],body=[fn],decorator_list=[])]
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected,type_ignores=[])),str(path),"exec"),ns)
    return ns[name] if klass is None else ns[klass]

class R113GatewayCapacity(unittest.TestCase):
    def make_gateway(self,tmp):
        ns={"json":json,"uuid":uuid,"datetime":datetime,"UTC":UTC,"Path":Path,"math":math,
            "ALLOWED_MODES":{"PAPER","REPLAY","MICRO_SIM"},
            "LIVE_MODE_TO_ACTION":{"FTMO_REAL":"FTMO_REAL_TRADE","LIVE":"LIVE_TRADE"},
            "TradeIntent":lambda **kw:SimpleNamespace(**kw),
            "audit_rule_application":lambda *args:{"decision":"ALLOW_FTMO_SIMULATION"},
            "require_defined_regime":lambda *args:(True,"OK"),
            "institutional_live_lock":lambda *args:{"decision":"BLOCK_LIVE"}}
        for name,file in [("validate_order_payload","safe_broker_adapter.py"),
                          ("simulate_fill","paper_fill_model.py"),
                          ("write_paper_broker_ledger","paper_broker_adapter.py"),
                          ("paper_route_order","paper_broker_adapter.py")]:
            extract(EXEC/file,name,ns)
        extract(GATEWAY,"write_execution_ledger",ns)
        cls=extract(GATEWAY,"submit_order",ns,"ExecutionGateway")
        obj=object.__new__(cls)
        obj.ledger_path=str(Path(tmp)/"execution.jsonl")
        obj.paper_broker_ledger_path=str(Path(tmp)/"broker.jsonl")
        obj.paper=SimpleNamespace(
            pre_trade_check=lambda *args:{"allowed":True,"decision":"ALLOW","session_id":"offline"},
            ftmo_config_path=None)
        obj.ftmo=SimpleNamespace(validate=lambda *args:(True,"OK"))
        obj.ftmo_config_valid={"valid":True,"hash":"offline"}
        obj.ftmo_ruleset={"version":"offline"}
        obj.risk=SimpleNamespace(validate=lambda *args:(True,"OK"))
        obj.adv=SimpleNamespace(review_trade=lambda *args:{"adversarial_passed":True,"decision":"OK"})
        obj.paper_capacity=Gate(Path(tmp)/"capacity.sqlite")
        obj.paper_capacity_max_daily_trades=1
        return obj,ns

    def test_second_fill_blocked_before_paper_broker(self):
        with tempfile.TemporaryDirectory(prefix="et665_r113_") as tmp:
            obj,ns=self.make_gateway(tmp)
            trade={"symbol":"TEST","side":"BUY","strategy_id":"TEST","entry":100.0,"stop":95.0,
                   "target":110.0,"risk_amount":1.0}
            first=obj.submit_order("PAPER",trade,{"regime":"DEFINED"},{"genome_id":"offline"})
            second=obj.submit_order("PAPER",trade,{"regime":"DEFINED"},{"genome_id":"offline"})
            self.assertEqual(first["decision"],"ACCEPT_SIMULATED_ORDER")
            self.assertEqual(second["decision"],"REJECT_ORDER")
            self.assertEqual(len(Path(obj.paper_broker_ledger_path).read_text().splitlines()),1)
            self.assertEqual(first["paper_broker"]["order"]["session_id"],"offline")
            self.assertEqual(first["paper_broker"]["order"]["capacity_order_id"],first["capacity_order_id"])
            self.assertEqual(second["capacity_decision"],"BLOCK_CAPACITY")

    def test_unknown_ledger_write_blocks_and_keeps_reservation(self):
        with tempfile.TemporaryDirectory(prefix="et665_r113_") as tmp:
            obj,ns=self.make_gateway(tmp)
            original=ns["paper_route_order"]
            def fail_broker(*args,**kwargs):
                raise OSError("simulated write failure")
            ns["paper_route_order"]=fail_broker
            trade={"symbol":"TEST","side":"BUY","strategy_id":"TEST","entry":100.0,"stop":95.0,
                   "target":110.0,"risk_amount":1.0}
            first=obj.submit_order("PAPER",trade,{"regime":"DEFINED"},{"genome_id":"offline"})
            ns["paper_route_order"]=original
            second=obj.submit_order("PAPER",trade,{"regime":"DEFINED"},{"genome_id":"offline"})
            self.assertEqual(first["decision"],"REJECT_ORDER")
            self.assertEqual(first["capacity_decision"],"BLOCK_BROKER_UNKNOWN")
            self.assertEqual(second["capacity_decision"],"BLOCK_CAPACITY")

if __name__=="__main__":
    unittest.main()
