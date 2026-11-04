"""Inventory Python stubs in a local repository checkout, without executing modules.

Usage: python tools/audit_trader_stubs.py --root . --output reports/trader_stub_inventory.json
Evidence classes are conservative: text hits are candidates, not certified stubs.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

MARKERS=('stub_active','not_implemented','not implemented','placeholder','todo','pass','raise NotImplementedError')
FOCUS=('trader','ftmo','portfolio','risk','execution','broker','institutional','market')

def scan(root):
    out=[];errors=[]
    for p in sorted(root.rglob('*.py')):
        rel=p.relative_to(root).as_posix()
        if any(x in p.parts for x in ('.git','.venv','venv','site-packages','__pycache__')):
            continue
        if not any(x in rel.lower() for x in FOCUS):continue
        try:
            raw=p.read_bytes()
            source=raw.decode('utf-8-sig')
            tree=ast.parse(source,filename=rel)
            hits=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.FunctionDef) or isinstance(node,ast.AsyncFunctionDef):
                    body=[n for n in node.body if not isinstance(n,ast.Expr) or not isinstance(n.value,ast.Constant) or not isinstance(n.value.value,str)]
                    if len(body)==1 and isinstance(body[0],ast.Pass):
                        hits.append({'line':node.lineno,'function':node.name,'reason':'PASS_ONLY'})
                    if len(body)==1 and isinstance(body[0],ast.Raise) and isinstance(body[0].exc,ast.Call) and isinstance(body[0].exc.func,ast.Name) and body[0].exc.func.id=='NotImplementedError':
                        hits.append({'line':node.lineno,'function':node.name,'reason':'NOT_IMPLEMENTED'})
                if isinstance(node,ast.Constant) and isinstance(node.value,str) and any(x in node.value.lower() for x in MARKERS[:5]):
                    hits.append({'line':node.lineno,'reason':'STRING_MARKER','value':node.value[:120]})
            if hits:
                out.append({'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'classification':'REQUIRES_MANUAL_REVIEW','hits':hits})
        except (OSError,UnicodeError,SyntaxError) as exc:
            errors.append({'path':rel,'error_type':type(exc).__name__})
    return {'schema':'TRADER_STUB_INVENTORY_V1','scope':'focused Python files in checkout','items':out,'errors':errors,'certified_replacements':0,'merge_allowed':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('.'));ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();data=scan(args.root.resolve());args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'candidates':len(data['items']),'errors':len(data['errors']),'output':str(args.output)}))

if __name__=='__main__':main()
