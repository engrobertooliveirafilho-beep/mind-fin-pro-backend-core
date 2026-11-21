"""STEP452 offline retrieval from caller-provided, traceable documents.

Does not access the network or invent search results.
"""
import math
import re
from collections import Counter

class RetrievalError(ValueError):
    pass

def _tokens(text):
    return re.findall(r'\w+', text.casefold(), flags=re.UNICODE)

def search(query, documents, limit=5):
    if not isinstance(query, str) or not _tokens(query):
        raise RetrievalError('nonempty query required')
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
        raise RetrievalError('limit must be 1..20')
    if not isinstance(documents, list):
        raise RetrievalError('documents must be a list')
    q = Counter(_tokens(query))
    seen = set()
    hits = []
    for doc in documents:
        if not isinstance(doc, dict):
            raise RetrievalError('invalid document')
        identifier, title, body = (doc.get(k) for k in ('source_id', 'title', 'text'))
        if not all(isinstance(x, str) and x.strip() for x in (identifier, title, body)):
            raise RetrievalError('source_id, title and text required')
        if identifier in seen:
            raise RetrievalError('duplicate source_id')
        seen.add(identifier)
        terms = Counter(_tokens(title + ' ' + body))
        matches = sum(min(n, terms.get(token, 0)) for token, n in q.items())
        if not matches:
            continue
        score = matches / sum(q.values())
        if not math.isfinite(score):
            raise RetrievalError('invalid score')
        hits.append({'source_id': identifier, 'title': title, 'snippet': body[:240], 'score': score})
    return sorted(hits, key=lambda hit: (-hit['score'], hit['source_id']))[:limit]
