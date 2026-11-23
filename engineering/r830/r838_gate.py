import ast

def audit(source):
    try: tree=ast.parse(source)
    except SyntaxError: return {'certified':False,'error':'syntax','findings':[]}
    findings=[]
    for fn in [n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]:
        for n in ast.walk(fn):
            if isinstance(n,ast.Return) and isinstance(n.value,ast.Constant) and n.value.value=='burst': findings.append((fn.name,'constant_burst'))
            if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ans' for t in n.targets) and isinstance(n.value,ast.Constant): findings.append((fn.name,'answer_override'))
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'train_sim','build_dataset'}: findings.append((fn.name,'synthetic_generator_call'))
    return {'certified':False,'error':None,'findings':sorted(set(findings))}
