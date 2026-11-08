"""R92: prove existing session accounting API can block the next PAPER trade.

Offline characterization only: manual record_trade_result is NOT a gateway fix.
"""
import ast
from datetime import datetime, UTC
import json
import math
from pathlib import Path
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "mind_trader/app/execution/paper_session.py"

class R92ExistingSessionContract(unittest.TestCase):
    def test_recorded_trade_blocks_next_trade_and_does_not_double_count_rejection(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        original = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PaperTradingSessionManager")
        wanted = {"_read_session", "_write_session", "_ledger", "pre_trade_check", "record_trade_result"}
        methods = [n for n in original.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
        cls = ast.ClassDef(name="PaperTradingSessionManager", bases=[], keywords=[], body=methods, decorator_list=[])
        ns = {"json": json, "uuid": uuid, "datetime": datetime, "UTC": UTC,
              "Path": Path, "math": math, "_now": lambda: datetime.now(UTC).isoformat()}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])), str(SOURCE), "exec"), ns)
        with tempfile.TemporaryDirectory(prefix="et665_r92_") as tmp:
            obj = object.__new__(ns["PaperTradingSessionManager"])
            obj.session_path = Path(tmp) / "session.json"
            obj.ledger_path = Path(tmp) / "day.jsonl"
            obj._write_session({"session_id": "offline", "status": "OPEN",
                                "trades": 0, "max_daily_trades": 1, "daily_pnl": 0.0,
                                "max_daily_loss": 100.0, "loss_streak": 0,
                                "ftmo_config_hash": "offline"})
            self.assertTrue(obj.pre_trade_check(1.0)["allowed"])
            result = obj.record_trade_result(0.0)
            self.assertEqual(result["decision"], "TRADE_RECORDED")
            self.assertEqual(obj._read_session()["trades"], 1)
            self.assertEqual(obj.pre_trade_check(1.0)["decision"], "BLOCK_MAX_DAILY_TRADES")
            self.assertEqual(len(obj.ledger_path.read_text().splitlines()), 1)

if __name__ == "__main__":
    unittest.main()
