import ast
import hashlib
import io
import tokenize

def inspect_source(raw):
    result = dict(sha256=hashlib.sha256(raw).hexdigest(), imports=[], certified=False)
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
        tree = ast.parse(raw.decode(encoding))
    except (SyntaxError, UnicodeError, LookupError):
        return dict(result, status='PARSE_FAILED')
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result['imports'].extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            result['imports'].append('.'*node.level+(node.module or ''))
    return dict(result, status='STATIC_INVENTORY_ONLY')
