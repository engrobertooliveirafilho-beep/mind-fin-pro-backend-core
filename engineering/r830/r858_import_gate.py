"""R858: Conservative import-time risk gate; inspected modules are never imported."""
import ast
RISK_NAMES=frozenset({'exec','eval','open','__import__','getattr','globals','locals','start_scheduler'})
RISK_ATTRS=frozenset({'mkdir','write_text','write_bytes','run','copy','start','Popen','system','remove','unlink','replace','rename'})
def audit(source):
    blocked={'status':'blocked','runtime_certified':False,'execution_authorized':False}
    if type(source) is not bytes or not source or len(source)>2000000:return {**blocked,'reason':'invalid_source'}
    try:tree=ast.parse(source.decode('utf-8'))
    except (SyntaxError,UnicodeDecodeError,ValueError):return {**blocked,'reason':'invalid_python'}
    aliases={}
    for node in tree.body:
        if isinstance(node,ast.Import):
            for a in node.names:aliases[a.asname or a.name]=a.name
        if isinstance(node,ast.ImportFrom):
            for a in node.names:aliases[a.asname or a.name]=(node.module or '')+'.'+a.name
    def resolve(expr):
        if isinstance(expr,ast.Name):return aliases.get(expr.id,expr.id)
        if isinstance(expr,ast.Attribute):return resolve(expr.value)+'.'+expr.attr
        return '<dynamic>'
    findings=set()
    def walk(node):
        for n in ast.walk(node):
            if isinstance(n,ast.Call):
                name=resolve(n.func)
                if name=='<dynamic>' or name.split('.')[-1] in RISK_NAMES|RISK_ATTRS:findings.add(name)
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            for x in [*n.decorator_list,*n.args.defaults,*[d for d in n.args.kw_defaults if d is not None],*([n.returns] if n.returns else [])]:walk(x)
        elif isinstance(n,ast.ClassDef):
            for x in [*n.decorator_list,*n.bases,*[v for kw in n.keywords for v in [kw.value]]]:walk(x)
            for x in n.body:
                if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    for z in [*x.decorator_list,*x.args.defaults,*[d for d in x.args.kw_defaults if d is not None]]:walk(z)
                else:walk(x)
        else:walk(n)
    if findings:return {**blocked,'reason':'import_time_risk','findings':sorted(findings)}
    return {'status':'candidate_only','runtime_certified':False,'execution_authorized':False}
