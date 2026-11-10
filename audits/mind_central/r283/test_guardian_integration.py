# R283 reproduction: execute this against local transcribed guardian_mind.py
# Dependencies are injected into sys.modules before import.
import sys, types, unittest
for name in ('app','app.cognition'):
 m=types.ModuleType(name);m.__path__=[];sys.modules[name]=m
sources={}
for module,obj in [('auto_explanation','engine'),('reality_model','reality_model'),('global_coherence','guardian'),('immunity','immune_system')]:
 m=types.ModuleType('app.cognition.'+module);o=types.SimpleNamespace();setattr(m,obj,o);sys.modules[m.__name__]=m;sources[module]=o
from guardian_mind import guardian_mind
from guardian_binding_gate import bound_scan,GuardianRejected
def set_state(explanation=None,reality=None,coherence=None,immunity=None):
 sources['auto_explanation'].last_explanation=explanation or {}
 sources['reality_model'].last_result=reality or {}
 sources['global_coherence'].last_check=coherence or {}
 sources['immunity'].last_scan=immunity or {}
B={'explanation':{'tags':[]},'reality':{'certainty':.7},'coherence':{'alerts':[]},'immunity':{'flags':[]}}
class T(unittest.TestCase):
 def setUp(self):set_state(**B)
 def test_valid(self):self.assertEqual(bound_scan(guardian_mind,**B)['protection_score'],1.)
 def test_missing_max(self):set_state();self.assertEqual(guardian_mind.scan()['protection_score'],1.)
 def test_missing_gate(self):
  with self.assertRaises(GuardianRejected):bound_scan(guardian_mind,**{**B,'reality':{}})
 def test_nan_gate(self):
  with self.assertRaises(GuardianRejected):bound_scan(guardian_mind,**{**B,'reality':{'certainty':float('nan')}})
 def test_stale_reality(self):
  with self.assertRaises(GuardianRejected):bound_scan(guardian_mind,**{**B,'reality':{'certainty':.2}})
 def test_stale_immune(self):
  with self.assertRaises(GuardianRejected):bound_scan(guardian_mind,**{**B,'immunity':{'flags':['x']}})
 def test_ethical(self):
  b={**B,'explanation':{'tags':['ethics_attention']}};set_state(**b)
  self.assertAlmostEqual(bound_scan(guardian_mind,**b)['protection_score'],.8)
 def test_low_certainty(self):
  b={**B,'reality':{'certainty':.2}};set_state(**b)
  self.assertAlmostEqual(bound_scan(guardian_mind,**b)['protection_score'],.8)
 def test_immune_flag(self):
  b={**B,'immunity':{'flags':['x']}};set_state(**b)
  self.assertAlmostEqual(bound_scan(guardian_mind,**b)['protection_score'],.9)
 def test_coherence(self):
  b={**B,'coherence':{'alerts':['x']}};set_state(**b)
  self.assertAlmostEqual(bound_scan(guardian_mind,**b)['protection_score'],.8)
 def test_invalid_output(self):
  original=guardian_mind.scan
  try:
   guardian_mind.scan=lambda:{'protection_score':float('nan')}
   with self.assertRaises(GuardianRejected):bound_scan(guardian_mind,**B)
  finally:guardian_mind.scan=original
 def test_prevalidation_does_not_mutate(self):
  guardian_mind._last_scan={'sentinel':True}
  with self.assertRaises(GuardianRejected):bound_scan(guardian_mind,**{**B,'reality':{}})
  self.assertEqual(guardian_mind.last_scan,{'sentinel':True})
if __name__=='__main__':unittest.main()
