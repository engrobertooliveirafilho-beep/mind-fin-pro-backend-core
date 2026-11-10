"""ET665.R347 — prove output-hash gate rejects fabricated attestations."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[2]/"experimental/et665_r346_real_agent_gate.py"
spec=importlib.util.spec_from_file_location("et665_r347_gate",SOURCE)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class HashIntegrity(unittest.TestCase):
    def test_real_output_hash_and_forged_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"agent.py"
            source.write_text("def run_dry(payload): return {}\n",encoding="utf-8")
            payload={"component":"monthly_cashflow","input_sha256":"a"*64}
            output={"net_cashflow":"4000.00"}
            digest=hashlib.sha256(json.dumps(output,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            result={"component":"monthly_cashflow","input_sha256":"a"*64,
                    "output":output,"output_sha256":digest,"processed_items":1}
            module=types.SimpleNamespace(__file__=str(source))
            dispatcher=types.SimpleNamespace(run_agent=lambda name,data: result)
            with patch.object(gate.importlib,"import_module",return_value=module):
                record=gate.verify_one("business_strategy_cashflow_agent",payload,dispatcher)
                self.assertEqual(record["status"],"PASS")
                result["output_sha256"]="0"*64
                with self.assertRaisesRegex(RuntimeError,"output hash"):
                    gate.verify_one("business_strategy_cashflow_agent",payload,dispatcher)
    def test_missing_output_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"agent.py"
            source.write_text("pass\n",encoding="utf-8")
            payload={"component":"monthly_cashflow","input_sha256":"a"*64}
            result={"component":"monthly_cashflow","input_sha256":"a"*64,
                    "output_sha256":"a"*64,"processed_items":1}
            module=types.SimpleNamespace(__file__=str(source))
            dispatcher=types.SimpleNamespace(run_agent=lambda name,data: result)
            with patch.object(gate.importlib,"import_module",return_value=module):
                with self.assertRaisesRegex(RuntimeError,"concrete output"):
                    gate.verify_one("business_strategy_cashflow_agent",payload,dispatcher)
if __name__=="__main__": unittest.main()
