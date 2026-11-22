"""Inspect recovered STEP177 without importing or running its FastAPI router."""
import ast
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / 'recovered/finance_steps/step177_static_status_route_original.py'

class Step177StaticRouteTests(unittest.TestCase):
    def test_original_is_static_route_not_finance_engine(self):
        source = PATH.read_text(encoding='utf-8')
        tree = ast.parse(source)
        methods = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        self.assertEqual([m.name for m in methods], ['run_step_177'])
        result = methods[0].body[0]
        self.assertIsInstance(result, ast.Return)
        data = ast.literal_eval(result.value)
        self.assertEqual(data, {'version':'step177-v1','step':177,'status':'active'})
        self.assertNotIn('certified', data)
        self.assertNotIn('orders', data)
    def test_no_order_or_broker_imports(self):
        tree = ast.parse(PATH.read_text(encoding='utf-8'))
        imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(len(imports), 1)
        self.assertIsInstance(imports[0], ast.ImportFrom)
        self.assertEqual(imports[0].module, 'fastapi')
        self.assertEqual([alias.name for alias in imports[0].names], ['APIRouter'])
