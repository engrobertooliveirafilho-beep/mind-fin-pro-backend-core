"""ET665.R343 isolated concrete component regression."""
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[2]/"experimental/et665_r343_cashflow.py"
spec=importlib.util.spec_from_file_location("et665_r343_cashflow",SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
run_dry=module.run_dry

class CashflowTests(unittest.TestCase):
    def test_real_component_profit(self):
        r=run_dry({'revenue':'10000.00','fixed_costs':'4000.00','variable_costs':'2000.00','cash_balance':'5000.00'})
        self.assertEqual(r['net_cashflow'],'4000.00')
        self.assertIsNone(r['runway_months'])
        self.assertFalse(r['promotion_authorized'])
    def test_real_component_burn(self):
        r=run_dry({'revenue':'1000.00','fixed_costs':'2500.00','variable_costs':'500.00','cash_balance':'9000.00'})
        self.assertEqual(r['net_cashflow'],'-2000.00')
        self.assertEqual(r['runway_months'],'4.50')
    def test_reject_nonfinite(self):
        for bad in ('NaN','Infinity','-1','1.001',True):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                run_dry({'revenue':bad,'fixed_costs':'0','variable_costs':'0','cash_balance':'0'})
if __name__=='__main__': unittest.main()
