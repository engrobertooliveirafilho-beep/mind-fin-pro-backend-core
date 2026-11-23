"""R832 offline AST audit; never imports target modules."""
import ast
from pathlib import Path
TARGETS={'capability_recovery_report','inspect_capability_module','_safe_call','_call_by_signature','import_module','__import__','eval','exec'}
def inspect_source(source):
    try: tree=ast.parse(source)
    except SyntaxError as e: return {'safe':False,'error':'syntax_error','line':e.lineno,'findings':[]}
    aliases={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for a in node.names: aliases[a.asname or a.name]=a.name
        elif isinstance(node,ast.ImportFrom):
            for a in node.names: aliases[a.asname or a.name]=(node.module or '')+'.'+a.name
    findings=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call): continue
        name=ast.unparse(node.func)
        root,sep,tail=name.partition('.')
        resolved=aliases.get(root,root)+(sep+tail if sep else '')
        if resolved.split('.')[-1] in TARGETS or name in {'fn','cls','inst'} or resolved.endswith('.store_social_memory'):
            findings.append({'line':node.lineno,'call':name,'resolved':resolved})
    return {'safe':not findings,'error':None,'findings':sorted(findings,key=lambda f:f['line'])}
def inspect_paths(paths):
    result={}
    for path in paths:
        try: result[str(path)]=inspect_source(Path(path).read_text(encoding='utf-8'))
        except (OSError,UnicodeError) as e: result[str(path)]={'safe':False,'error':type(e).__name__,'findings':[]}
    return result
