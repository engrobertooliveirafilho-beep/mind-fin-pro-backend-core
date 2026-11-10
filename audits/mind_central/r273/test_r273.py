import unittest
from secure_cognitive_gateway import execute,GateRejected
P={'user_benefit':.7,'safety':.9,'long_term':.8,'cashflow':.5,'learning':.6}
class Spy:
    def __init__(self):self.calls=0
    def decide(self,x):self.calls+=1;return x
class Cases(unittest.TestCase):
    def reject(self,p):
        e=Spy()
        with self.assertRaises(GateRejected):execute('will',e,p)
        self.assertEqual(e.calls,0)
    def test_duplicate_ids(self):self.reject({'options':[{'id':'a','scores':P},{'id':'a','scores':P}]})
    def test_missing_id(self):self.reject({'options':[{'scores':P}]})
    def test_empty_id(self):self.reject({'options':[{'id':' ','scores':P}]})
    def test_zero_weights(self):self.reject({'options':[{'id':'a','scores':P}],'weights':{k:0 for k in P}})
    def test_nan_weights(self):self.reject({'options':[{'id':'a','scores':P}],'weights':{**P,'safety':float('nan')}})
    def test_valid(self):
        e=Spy();execute('will',e,{'options':[{'id':'a','scores':P}]});self.assertEqual(e.calls,1)
if __name__=='__main__':unittest.main()
