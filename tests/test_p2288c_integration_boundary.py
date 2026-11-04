"""Read-only integration boundary tests against institutional runtime contracts.

No broker invocation and no production wiring modification.
"""
import ast
import unittest
from pathlib import Path
from mind_trader.research import p2288c_corrected as evaluator

ROOT = Path(__file__).resolve().parents[1]

class P2288CIntegrationBoundaryTests(unittest.TestCase):
    def test_evaluator_does_not_import_runtime_or_broker(self):
        tree = ast.parse((ROOT / 'mind_trader/research/p2288c_corrected.py').read_text())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        self.assertFalse(any(x.startswith(('app.', 'MetaTrader5', 'ccxt', 'requests')) for x in imports))

    def test_institutional_wiring_not_modified_to_load_research(self):
        path = ROOT / 'app/runtime/mind_trader_institutional_wiring.py'
        tree = ast.parse(path.read_text())
        names = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value,str)]
        self.assertNotIn('mind_trader.research.p2288c_corrected', names)

    def test_missing_cost_fails_closed(self):
        q={'symbol':'GER40','timeframe':'H1','strategy':'SESSION_TREND','session_filter':'ANY','volatility_filter':'ANY','spread_filter':'ANY','trend_filter':'ANY','mode':'PAPER_ONLY','real_orders':'FORBIDDEN'}
        with self.assertRaises(ValueError):
            evaluator.evaluate([q],{('GER40','H1'):[{}]*1000},{})

    def test_runtime_stub_is_not_certified(self):
        path=ROOT/'app/runtime/mind_trader_institutional_gate.py'
        text=path.read_text()
        self.assertIn('stub_active',text)
        self.assertNotIn('financial_certified',text)

if __name__ == '__main__':
    unittest.main()
