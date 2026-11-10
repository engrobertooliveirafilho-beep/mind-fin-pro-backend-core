import unittest
from secure_cognitive_gateway import execute, GateRejected
P={'user_benefit':.7,'safety':.9,'long_term':.8,'cashflow':.5,'learning':.6}
class Spy:
 def __init__(self):self.calls=0
 def decide(self,x):self.calls+=1;return x
class Regression(unittest.TestCase):
 def reject(self,p):
  s=Spy()
  with self.assertRaises(GateRejected):execute('will',s,p)
  self.assertEqual(s.calls,0)
 def test_ambiguous_id_name(self):self.reject({'options':[{'id':'a','name':'b','scores':P}]})
 def test_whitespace_duplicate(self):self.reject({'options':[{'id':'a','scores':P},{'id':' a ','scores':P}]})
 def test_partial_weights(self):self.reject({'options':[{'id':'a','scores':P}],'weights':{'safety':1}})
 def test_extra_weights(self):self.reject({'options':[{'id':'a','scores':P}],'weights':{**P,'untrusted':1}})
 def test_valid_weight_vector(self):
  s=Spy();execute('will',s,{'options':[{'id':'a','scores':P}],'weights':P});self.assertEqual(s.calls,1)
 def test_distinct_ids(self):
  s=Spy();execute('will',s,{'options':[{'id':'a','scores':P},{'id':'b','scores':P}]});self.assertEqual(s.calls,1)
if __name__=='__main__':unittest.main()
