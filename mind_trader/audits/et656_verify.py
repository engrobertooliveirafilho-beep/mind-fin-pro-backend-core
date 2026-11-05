"""ET-656: deterministic local audit of exact checked-out GitHub branch; no network/broker.
Usage: python mind_trader/audits/et656_verify.py
Run from repository root after checkout. Exit nonzero unless tests and source hashes pass.
"""
from pathlib import Path
from hashlib import sha256
import ast,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PKG=ROOT/'mind_trader'/'ftmo_paper_execution'
NAMES=('ftmo_paper_guard','ftmo_pretrade_v2','portfolio_runtime','ftmo_execution_v4','ftmo_execution_v5','ftmo_execution_v6','certification_gate_v7')
TESTS=('mind_trader/tests/test_et651_paper_execution_chain.py','mind_trader/tests/test_et653_paper_e2e.py')
def main():
    evidence={'scope':'EXACT_CHECKOUT_PAPER_ONLY','real_orders':0,'ftmo_release':'BLOCKED','source_sha256':{},'dependencies':{},'tests':None,'passed':False}
    for name in NAMES:
        path=PKG/(name+'.py')
        if not path.is_file(): raise SystemExit('MISSING: '+str(path))
        raw=path.read_bytes()
        evidence['source_sha256'][str(path.relative_to(ROOT))]=sha256(raw).hexdigest()
        tree=ast.parse(raw,filename=str(path))
        deps=sorted({n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.level==1 and n.module})
        if any(d not in NAMES for d in deps): raise SystemExit('UNEXPECTED DEPENDENCY: '+name)
        evidence['dependencies'][name]=deps
    for test in TESTS:
        if not (ROOT/test).is_file(): raise SystemExit('MISSING TEST: '+test)
    p=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'mind_trader'/'tests'),'-p','test_et65*_*.py'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
    evidence['tests']={'exit_code':p.returncode,'output':p.stdout[-12000:]}
    evidence['passed']=p.returncode==0
    output=ROOT/'mind_trader'/'audits'/'ET656_RUNTIME_EVIDENCE.json'
    output.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'passed':evidence['passed'],'files':len(NAMES),'evidence':str(output)},ensure_ascii=False))
    return 0 if evidence['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
