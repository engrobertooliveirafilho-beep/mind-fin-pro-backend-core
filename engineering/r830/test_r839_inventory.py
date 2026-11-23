import unittest,json
from r839_inventory import manifest_gate,inspect_module,classify_step_path,step_registry_gate,source_duplicates,BUCKETS
class TestR839(unittest.TestCase):
 def setUp(self):
  self.m={'buckets':{k:['app.'+k.lower()] for k in BUCKETS},'counts':{k:1 for k in BUCKETS},'policy':{'delete_files':False,'quarantine_type':'logical_manifest_only','orphaned_modules_policy':'do_not_integrate_without_explicit_revalidation','active_modules_may_be_used':list(BUCKETS[:-1])}}
  self.e={'id':'s1','path_canonical':'steps/step1.py','status':'VERIFIED_SOURCE','source_bucket_prefix':'COGNITIVE'}
 def test_manifest(self):self.assertTrue(manifest_gate(self.m)['valid'])
 def test_manifest_json(self):self.assertTrue(manifest_gate(json.dumps(self.m))['valid'])
 def test_no_orphans(self):self.assertFalse(manifest_gate(self.m)['promote_orphans'])
 def test_duplicate(self):
  self.m['buckets'][BUCKETS[1]]=self.m['buckets'][BUCKETS[0]];self.assertFalse(manifest_gate(self.m)['valid'])
 def test_policy(self):
  self.m['policy']['delete_files']=True;self.assertFalse(manifest_gate(self.m)['valid'])
 def test_imports(self):self.assertEqual(inspect_module('import os')['imports'],['os'])
 def test_functions(self):self.assertEqual(inspect_module('def f(): pass')['functions'],['f'])
 def test_classes(self):self.assertEqual(inspect_module('class C: pass')['classes'],['C'])
 def test_dynamic(self):self.assertEqual(inspect_module('eval("1")')['dynamic_calls'][0]['call'],'eval')
 def test_parse(self):self.assertFalse(inspect_module('def (')['parsed'])
 def test_step(self):self.assertTrue(classify_step_path('zip/steps/step1.py')['cognitive'])
 def test_traversal(self):self.assertEqual(classify_step_path('../steps/step1.py')['status'],'INVALID')
 def test_registry(self):self.assertTrue(step_registry_gate([self.e])['valid'])
 def test_registry_duplicate(self):self.assertFalse(step_registry_gate([self.e,self.e])['valid'])
 def test_registry_claim(self):self.assertFalse(step_registry_gate([dict(self.e,status='TESTED_OFFLINE')])['valid'])
 def test_duplicate_source(self):self.assertEqual(source_duplicates({'a':'x','b':'x'}),[['a','b']])
if __name__=='__main__':unittest.main()
