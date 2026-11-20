"""Offline-only integration of P1625 allocation and P1626X validation."""
import hashlib
import json
from pathlib import Path
from decimal import Decimal
from app.runtime.p1625_safe_portfolio import allocate
from app.runtime.p1626x_paper_gate import validate

MAX_SOURCE_BYTES = 20_000_000

def run_file(source):
    source = Path(source)
    if not source.is_file() or source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError('source missing or too large')
    raw = source.read_bytes()
    if not raw or len(raw) > MAX_SOURCE_BYTES:
        raise ValueError('empty/oversize source')
    edges = json.loads(raw)
    portfolio = allocate(edges)
    research = validate(portfolio)
    if research['edges'] != len(portfolio):
        raise ValueError('P1625/P1626X count mismatch')
    scores = {x['edge_id']: Decimal(x['research_allocation_score']) for x in research['scores']}
    if any(Decimal(str(p['portfolio_score'])) != scores[p['edge_id']] for p in portfolio):
        raise ValueError('P1625/P1626X score mismatch')
    if abs(sum((Decimal(str(p['paper_weight'])) for p in portfolio), Decimal(0))-1) > Decimal('0.000001'):
        raise ValueError('portfolio weights invalid')
    return {'status':'PAPER_PIPELINE_OFFLINE_PASS', 'edges':len(portfolio),
            'source_sha256':hashlib.sha256(raw).hexdigest(),
            'real_orders':'FORBIDDEN', 'allocation_authorized':False,
            'e2e_certified':False}
