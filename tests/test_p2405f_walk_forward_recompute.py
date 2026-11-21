import importlib.util, pathlib, unittest
p=pathlib.Path(__file__).resolve().parents[1]/"src"/"revisions"/"p2405f_walk_forward_recompute.py"
s=importlib.util.spec_from_file_location("wf",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
W=[dict(start=i*100,end=(i+1)*100) for i in range(5)]
def trades(r=1.0):
 return [dict(entry_i=i*100+j*2,exit_i=i*100+j*2+1,r=r,real_execution_allowed=False) for i in range(5) for j in range(6)]
class TestWF(unittest.TestCase):
 def test_positive(self): self.assertTrue(m.evaluate_walk_forward(trades())["research_qualified"])
 def test_runtime_disabled(self): self.assertFalse(m.evaluate_walk_forward(trades())["runtime_allowed"])
 def test_real_disabled(self): self.assertFalse(m.evaluate_walk_forward(trades())["real_execution_allowed"])
 def test_negative(self): self.assertFalse(m.evaluate_walk_forward(trades(-1))["research_qualified"])
 def test_overlap(self):
  with self.assertRaises(ValueError): m.evaluate_walk_forward(trades(),[dict(start=0,end=110)]+W[1:])
 def test_missing(self):
  with self.assertRaises(ValueError): m.evaluate_walk_forward([],W)
 def test_fake_flag(self):
  t=trades();t[0]["real_execution_allowed"]=True
  with self.assertRaises(ValueError): m.evaluate_walk_forward(t,W)
 def test_boundary(self):
  t=trades();t[0]["exit_i"]=101
  with self.assertRaises(ValueError): m.evaluate_walk_forward(t,W)
 def test_nan(self):
  t=trades();t[0]["r"]=float("nan")
  with self.assertRaises(ValueError): m.evaluate_walk_forward(t,W)
 def test_wrong_order(self):
  t=trades();t[0],t[-1]=t[-1],t[0]
  with self.assertRaises(ValueError): m.evaluate_walk_forward(t,W)
