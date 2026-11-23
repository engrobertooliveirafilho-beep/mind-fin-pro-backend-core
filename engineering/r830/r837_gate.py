"""Static gate for duplicated humanization sources. Never imports target."""
import ast

def audit(source):
    try:
        tree=ast.parse(source)
    except SyntaxError:
        return {'certified':False,'error':'syntax','findings':[]}
    funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    findings=[]
    for name,node in funcs.items():
        for n in ast.walk(node):
            if isinstance(n,ast.Return) and isinstance(n.value,ast.Constant) and n.value.value == 'burst':
                findings.append((name,'constant_burst'))
            if isinstance(n,ast.Assign):
                for target in n.targets:
                    if isinstance(target,ast.Name) and target.id=='ans' and isinstance(n.value,ast.Constant):
                        findings.append((name,'answer_override'))
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'train_sim','build_dataset'}:
                findings.append((name,'synthetic_generator_call'))
    return {'certified':False,'error':None,'functions':sorted(funcs),'findings':sorted(set(findings))}

def duplicate_groups(path_to_sha):
    groups={}
    for path,sha in path_to_sha.items(): groups.setdefault(sha,[]).append(path)
    return [sorted(paths) for paths in groups.values() if len(paths)>1]
