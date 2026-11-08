"""ET665.R108: characterize actual PAPER broker JSONL ledger schema, fail closed.

Source is parsed only; no trading imports or execution.
"""
import ast
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[3]
BROKER=ROOT/"products/eldora_trader/mind_trader/app/execution/paper_broker_adapter.py"
GATEWAY=ROOT/"products/eldora_trader/mind_trader/app/execution/gateway.py"

def schema_audit():
    broker=ast.parse(BROKER.read_text(encoding="utf-8"))
    gateway=ast.parse(GATEWAY.read_text(encoding="utf-8"))
    funcs={node.name:node for node in broker.body if isinstance(node,ast.FunctionDef)}
    ledger=funcs["write_paper_broker_ledger"]
    route=funcs["paper_route_order"]
    gw=next(node for node in gateway.body if isinstance(node,ast.ClassDef) and node.name=="ExecutionGateway")
    submit=next(node for node in gw.body if isinstance(node,ast.FunctionDef) and node.name=="submit_order")
    ledger_keys=set()
    for node in ast.walk(ledger):
        if isinstance(node,ast.Subscript) and isinstance(node.value,ast.Name) and node.value.id=="event" and isinstance(node.slice,ast.Constant):
            ledger_keys.add(node.slice.value)
    route_events=[]
    for node in ast.walk(route):
        if isinstance(node,ast.Dict):
            keys=[k.value for k in node.keys if isinstance(k,ast.Constant)]
            if "decision" in keys:
                route_events.append(set(keys))
    has_gateway_order_key=any(isinstance(n,ast.Constant) and n.value in ("paper_order_id","order_id") for n in ast.walk(submit))
    return {"ledger_keys":ledger_keys,"route_events":route_events,"gateway_order_key":has_gateway_order_key}

def reconcile_actual_broker_rows(rows, session, expected_filled_ids):
    """Read-only validator; never mutates capacity or assumes session linkage."""
    if not isinstance(rows,list) or not isinstance(expected_filled_ids,set):
        return "BLOCK_INVALID_INPUT"
    ids=[]
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get("paper_order_id"),str) or not row["paper_order_id"]:
            return "BLOCK_INVALID_BROKER_ROW"
        if row.get("production")!="BLOCKED" or row.get("live")!="FORBIDDEN":
            return "BLOCK_UNSAFE_BROKER_ROW"
        if row.get("decision")=="PAPER_ORDER_ACCEPTED":
            if row.get("order_status")!="PAPER_FILLED_SIMULATED" or not isinstance(row.get("fill"),dict) or row["fill"].get("filled") is not True:
                return "BLOCK_UNCONFIRMED_FILL"
            ids.append(row["paper_order_id"])
    if len(ids)!=len(set(ids)):
        return "BLOCK_DUPLICATE_BROKER_ORDER_ID"
    # Current broker ledger has no session identifier or reservation key.
    # Equality by broker UUID alone is insufficient to establish session ownership.
    return "BLOCK_UNLINKED_SESSION_RESERVATION"

class R108ActualSchema(unittest.TestCase):
    def test_actual_source_exposes_missing_linkage(self):
        schema=schema_audit()
        self.assertIn("paper_order_id",schema["ledger_keys"])
        self.assertIn("ts",schema["ledger_keys"])
        self.assertFalse(schema["gateway_order_key"])
        self.assertTrue(any("order_status" in keys for keys in schema["route_events"]))

    def test_actual_rows_fail_closed_without_session_join(self):
        row={"paper_order_id":"uuid-1","decision":"PAPER_ORDER_ACCEPTED","order_status":"PAPER_FILLED_SIMULATED","fill":{"filled":True},"production":"BLOCKED","live":"FORBIDDEN"}
        self.assertEqual(reconcile_actual_broker_rows([row],"s",{"uuid-1"}),"BLOCK_UNLINKED_SESSION_RESERVATION")
        self.assertEqual(reconcile_actual_broker_rows([row,row],"s",{"uuid-1"}),"BLOCK_DUPLICATE_BROKER_ORDER_ID")
        self.assertEqual(reconcile_actual_broker_rows([{**row,"fill":{"filled":False}}],"s",{"uuid-1"}),"BLOCK_UNCONFIRMED_FILL")
        self.assertEqual(reconcile_actual_broker_rows([{**row,"live":"ALLOWED"}],"s",{"uuid-1"}),"BLOCK_UNSAFE_BROKER_ROW")

if __name__=="__main__":
    unittest.main()
