"""R839 offline inventory and step reconciliation; no legacy runtime imports."""
import ast,json,re,hashlib
from collections import defaultdict
BUCKETS=('ACTIVE_IN_PIPELINE','ACTIVE_IN_WHATSAPP_ADAPTER','ACTIVE_OUTSIDE_PIPELINE','ORPHANED_OR_UNUSED')
def manifest_gate(raw):
 try:
  obj=json.loads(raw) if isinstance(raw,str) else raw
  if set(obj['buckets'])!=set(BUCKETS): raise ValueError('buckets')
  seen=set();counts={}
  for b in BUCKETS:
   vals=obj['buckets'][b]
   if not isinstance(vals,list) or any(not isinstance(x,str) or not re.fullmatch(r'app(?:\.[A-Za-z_][A-Za-z_0-9]*)+',x) for x in vals): raise ValueError('names')
   if len(set(vals))!=len(vals) or seen.intersection(vals): raise ValueError('duplicates')
   seen.update(vals);counts[b]=len(vals)
  if counts!=obj['counts']: raise ValueError('counts')
  p=obj['policy']
  if p.get('delete_files') is not False or p.get('quarantine_type')!='logical_manifest_only' or p.get('orphaned_modules_policy')!='do_not_integrate_without_explicit_revalidation': raise ValueError('policy')
  if set(p.get('active_modules_may_be_used',[]))!=set(BUCKETS[:-1]): raise ValueError('active')
  return {'valid':True,'counts':counts,'total':len(seen),'promote_orphans':False}
 except (TypeError,ValueError,KeyError,AttributeError): return {'valid':False,'promote_orphans':False}
def inspect_module(source):
 try: tree=ast.parse(source)
 except (SyntaxError,TypeError): return {'parsed':False,'certified':False,'imports':[],'functions':[],'classes':[],'dynamic_calls':[]}
 imports=[];funcs=[];classes=[];calls=[]
 for n in ast.walk(tree):
  if isinstance(n,ast.Import): imports.extend(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom): imports.append('.'*n.level+(n.module or ''))
  elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): funcs.append(n.name)
  elif isinstance(n,ast.ClassDef): classes.append(n.name)
  elif isinstance(n,ast.Call):
   name=ast.unparse(n.func)
   if name in {'eval','exec','__import__','importlib.import_module','getattr','globals','locals','runpy.run_module','subprocess.run','os.system'}: calls.append({'line':n.lineno,'call':name})
 return {'parsed':True,'certified':False,'imports':sorted(set(imports)),'functions':sorted(set(funcs)),'classes':sorted(set(classes)),'dynamic_calls':calls}
def classify_step_path(path):
 if not isinstance(path,str) or not path.strip(): return {'status':'INVALID','cognitive':False}
 path=path.replace('\\','/').lower()
 if '..' in path.split('/'): return {'status':'INVALID','cognitive':False}
 ok=bool(re.search(r'(?:^|/)steps/step[^/]*\.(?:py|md|txt|json)$',path))
 return {'status':'COGNITIVE_CANDIDATE' if ok else 'UNCLASSIFIED','cognitive':ok}
def step_registry_gate(entries):
 if not isinstance(entries,list): return {'valid':False,'errors':['not_list']}
 errors=[];ids=set();paths=set()
 for i,e in enumerate(entries):
  if not isinstance(e,dict) or set(e)!={'id','path_canonical','status','source_bucket_prefix'}: errors.append(f'{i}:schema');continue
  ident,path,status,bucket=(e[k] for k in ('id','path_canonical','status','source_bucket_prefix'))
  if not all(isinstance(v,str) and v.strip() for v in (ident,path,status,bucket)): errors.append(f'{i}:empty');continue
  if ident in ids or path in paths: errors.append(f'{i}:duplicate')
  ids.add(ident);paths.add(path)
  if classify_step_path(path)['status']=='INVALID': errors.append(f'{i}:path')
  if status not in {'CANDIDATE','VERIFIED_SOURCE','BLOCKED'}: errors.append(f'{i}:status')
 return {'valid':not errors,'errors':errors,'total':len(entries),'runtime_certified':False}
def source_duplicates(mapping):
 groups=defaultdict(list)
 for path,source in mapping.items(): groups[hashlib.sha256(source.encode('utf-8')).hexdigest()].append(path)
 return [sorted(paths) for paths in groups.values() if len(paths)>1]
