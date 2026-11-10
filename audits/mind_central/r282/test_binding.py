import unittest
from guardian_binding_gate import bound_scan, GuardianRejected
from guardian_gate import checked_scan
B={'explanation':{'tags':[]},'reality':{'certainty':.7},'coherence':{'alerts':[]},'immunity':{'flags':[]}}
class Guardian:
 def __init__(self,source=None,score=1.,alerts=None):self.source=source;self.score=score;self.alerts=alerts;self.calls=0
 def scan(self):
  self.calls+=1
  s=self.source if self.source is not None else B
  return {'sources':{'explanation_tags':s['explanation']['tags'],'reality':s['reality'],'immune':s['immunity'],'coherence':s['coherence']},'alerts':[] if self.alerts is None else self.alerts,'protection_score':self.score}
class Tests(unittest.TestCase):
 def test_valid(self):self.assertEqual(bound_scan(Guardian(),**B)['protection_score'],1.)
 def test_r281_does_not_bind_sources(self):self.assertEqual(checked_scan(Guardian(source={**B,'reality':{'certainty':.1}}),**B)['protection_score'],1.)
 def test_r282_rejects_source_mismatch(self):
  with self.assertRaises(GuardianRejected):bound_scan(Guardian(source={**B,'reality':{'certainty':.1}}),**B)
 def test_rejects_score_mismatch(self):
  with self.assertRaises(GuardianRejected):bound_scan(Guardian(score=.8),**B)
 def test_rejects_alert_mismatch(self):
  with self.assertRaises(GuardianRejected):bound_scan(Guardian(alerts=['fake']),**B)
 def test_missing_source(self):
  class G:
   def scan(self):return {'protection_score':1.}
  with self.assertRaises(GuardianRejected):bound_scan(G(),**B)
 def test_nan_preblocked(self):
  g=Guardian()
  with self.assertRaises(GuardianRejected):bound_scan(g,**{**B,'reality':{'certainty':float('nan')}})
  self.assertEqual(g.calls,0)
 def test_missing_telemetry_preblocked(self):
  g=Guardian()
  with self.assertRaises(GuardianRejected):bound_scan(g,**{**B,'immunity':{}})
  self.assertEqual(g.calls,0)
 def test_rejects_extra_source(self):
  class G:
   def scan(self):
    r=Guardian().scan();r['sources']['unknown']=1;return r
  with self.assertRaises(GuardianRejected):bound_scan(G(),**B)
 def test_rejects_bool_score(self):
  with self.assertRaises(GuardianRejected):bound_scan(Guardian(score=True),**B)
 def test_valid_ethical_alert(self):
  b={**B,'explanation':{'tags':['ethics_attention']}}
  self.assertEqual(bound_scan(Guardian(source=b,score=.8,alerts=['ethics_attention']),**b)['protection_score'],.8)
 def test_valid_low_certainty(self):
  b={**B,'reality':{'certainty':.2}}
  self.assertEqual(bound_scan(Guardian(source=b,score=.8,alerts=['low_reality_certainty']),**b)['protection_score'],.8)
if __name__=='__main__':unittest.main()
