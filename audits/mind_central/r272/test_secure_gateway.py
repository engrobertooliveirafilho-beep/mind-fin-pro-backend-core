import unittest
from secure_cognitive_gateway import execute, GateRejected
P={'user_benefit':.7,'safety':.9,'long_term':.8,'cashflow':.5,'learning':.6}
E={'purpose_alignment':.8,'reality_certainty':.7,'ethics':.9}
class Fake:
    def __init__(self): self.calls=0
    def evaluate_action(self,x): self.calls+=1; return x
    def build_explanation(self,x): self.calls+=1; return x
    def decide(self,x): self.calls+=1; return x
class Tests(unittest.TestCase):
    def reject(self,kind,payload):
        f=Fake()
        with self.assertRaises(GateRejected): execute(kind,f,payload)
        self.assertEqual(f.calls,0)
    def test_valid_purpose(self):
        f=Fake(); self.assertEqual(execute('purpose',f,{'scores':P})['scores'],P); self.assertEqual(f.calls,1)
    def test_valid_explanation(self):
        f=Fake(); self.assertEqual(execute('explanation',f,{'scores':E})['scores'],E); self.assertEqual(f.calls,1)
    def test_valid_will(self):
        f=Fake(); self.assertEqual(execute('will',f,{'options':[{'id':'safe','scores':P}]})['options'][0]['id'],'safe'); self.assertEqual(f.calls,1)
    def test_reject_real_orders(self): self.reject('purpose',{'scores':P,'authorization':'REAL_ORDERS'})
    def test_reject_meta(self): self.reject('will',{'options':[{'id':'x','scores':P,'meta':{'authorization':'live'}}]})
    def test_reject_unknown_engine(self): self.reject('broker',{'scores':P})
    def test_reject_forbidden_name(self): self.reject('will',{'options':[{'id':'mt5_order_send','scores':P}]})
    def test_reject_nonfinite(self): self.reject('purpose',{'scores':{**P,'safety':float('nan')}})
    def test_reject_missing_score(self): self.reject('explanation',{'scores':{'ethics':.9}})
    def test_reject_extra_field(self): self.reject('explanation',{'scores':E,'mode':'production'})
    def test_reject_nested_authority(self): self.reject('will',{'options':[{'id':'x','scores':P,'authorization':'real_orders'}]})
    def test_reject_boolean(self): self.reject('purpose',{'scores':{**P,'safety':True}})
    def test_reject_invalid_options(self): self.reject('will',{'options':[]})
    def test_reject_oversized_options(self): self.reject('will',{'options':[{'scores':P}]*101})
    def test_reject_text_type(self): self.reject('purpose',{'scores':P,'description':{'role':'admin'}})
if __name__=='__main__': unittest.main()
