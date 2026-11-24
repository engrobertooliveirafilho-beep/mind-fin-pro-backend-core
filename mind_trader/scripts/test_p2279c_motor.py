import unittest, tempfile
from pathlib import Path
import p2279c_mass_backtest as m
class TestMotor(unittest.TestCase):
    def test_cost(self):
        rows=[dict(open=100+i%20,close=100+i%20) for i in range(1000)]
        a=m.backtest(rows,'SMA_CROSS','2,5',round_trip_cost=0.1)
        b=m.backtest(rows,'SMA_CROSS','2,5',round_trip_cost=0.2)
        self.assertIsNotNone(a); self.assertIsNotNone(b)
        self.assertAlmostEqual(a['netprofit']-b['netprofit'],a['trades']*.1,places=5)
    def test_bad_data(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.csv'; p.write_text('time,open,high,low,close\n2026-01-01,1,2,0,1\n')
            with self.assertRaises(ValueError): m.read_rows(p)
    def test_missing(self):
        with tempfile.TemporaryDirectory() as d:
            r=m.run(d,{})
            self.assertEqual(len(r['blocked']),65); self.assertEqual(r['results'],[])
if __name__=='__main__': unittest.main()
