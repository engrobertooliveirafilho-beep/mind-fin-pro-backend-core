"""V8 read-only PAPER consolidation, adapted from Drive 1f3D5QtQSKFyYQMopRujfzjiT1Sydah6q.

Explicit source/output paths; never overwrites original Drive files. Not FTMO certification.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

REQUIRED=('ftmo_paper_guard.py','ftmo_pretrade_v2.py','portfolio_runtime.py',
          'ftmo_execution_v4.py','ftmo_execution_v5.py','ftmo_execution_v6.py',
          'certification_gate_v7.py')
GATES=('canonical_runtime_hash_verified','all_motors_reconciled',
       'end_to_end_integration_pass','ftmo_rules_current_verified',
       'historical_oos_pass','forward_demo_30_90d_pass','broker_costs_verified',
       'daily_and_total_loss_guard_verified','explicit_human_authorization')

def run(source, out, *, package_root=None):
    source=Path(source).resolve()
    out=Path(out).resolve()
    if source == out or source in out.parents:
        raise ValueError('output must not modify source tree')
    if not source.is_dir():
        raise ValueError('source directory does not exist')
    out.mkdir(parents=True,exist_ok=True)
    evidence=[]
    for name in REQUIRED:
        path=source/name
        evidence.append({'module':name,'present':path.is_file(),
                         'sha256':sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
                         'authority':'isolated_paper_candidate_not_canonical'})
    tests=sorted(source.glob('test_*.py'))
    ready=all(x['present'] for x in evidence) and bool(tests)
    result=None
    if ready:
        paths=[str(source)]
        if package_root is not None:
            paths.append(str(Path(package_root).resolve()))
        env={**os.environ,'PYTHONPATH':os.pathsep.join(paths)}
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(source),
                               '-p','test_*.py','-v'],capture_output=True,text=True,
                              timeout=90,cwd=str(source),env=env)
    (out/'REGRESSION_V8.txt').write_text(
        result.stdout+'\n'+result.stderr if result else
        'BLOCKED: missing source modules or test files\n',encoding='utf-8')
    gate={k:False for k in GATES}
    audit={'version':'V8','scope':'READ_ONLY_CONSOLIDATION','modules':evidence,
           'test_files':[x.name for x in tests],
           'regression_returncode':result.returncode if result else None,
           'all_sources_present':all(x['present'] for x in evidence),
           'ftmo_gate_evidence':gate,'ftmo_release':'BLOCKED','real_orders':0,
           'canonical_integration':'NOT_VERIFIED','historical_motors':'NOT_FULLY_RECONCILED',
           'next_required':'CANONICAL_RUNTIME_HASH_AND_WIRING_E2E'}
    (out/'CONSOLIDATION_V8.json').write_text(
        json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    manifest={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())
              if p.is_file() and p.name!='SHA256_V8.json'}
    (out/'SHA256_V8.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'regression_returncode':result.returncode if result else None,
                      'modules':len(evidence),'test_files':len(tests),'ftmo_release':'BLOCKED'}))
    return result.returncode if result else 2

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--package-root',type=Path)
    args=parser.parse_args()
    raise SystemExit(run(args.source,args.out,package_root=args.package_root))
