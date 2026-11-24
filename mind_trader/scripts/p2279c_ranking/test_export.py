import unittest,tempfile,csv
from pathlib import Path
from export import export_reports
class ExportTest(unittest.TestCase):
    def test_reports(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'out'
            row=dict(symbol='EURUSD',timeframe='H1',strategy='EMA_CROSS',params='9,34',pf=2,trades=45,winrate=50,maxdd=1,netprofit=2)
            r=dict(results=[row],blocked=[('XAUUSD','D1','missing')])
            self.assertEqual(export_reports(r,p)['clean_results'],1)
            with (p/'tier_A.csv').open() as f: self.assertEqual(next(csv.DictReader(f))['real_orders'],'FORBIDDEN')
            with (p/'tier_B.csv').open() as f: self.assertEqual(list(csv.DictReader(f)),[])
            with self.assertRaises(FileExistsError): export_reports(r,p)
