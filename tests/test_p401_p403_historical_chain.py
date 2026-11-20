"""P401H -> P402 -> P403 integration regression against historical Drive exports.

Set ELDORA_HISTORICAL_DIR to a read-only directory containing:
p401h_top10_timeframe_balanced.json, p402_shadow_routes.json,
p403_500_master_report.json. No synthetic historical certification.
"""
import json
import os
from pathlib import Path
import pytest
from app.runtime.p402_shadow_safe import route_shadow
from app.runtime.p403_safe import score_routes

@pytest.fixture
def historical():
    folder=os.getenv('ELDORA_HISTORICAL_DIR')
    if not folder:
        pytest.skip('Original Drive exports required: ELDORA_HISTORICAL_DIR')
    root=Path(folder)
    def read(name):
        return json.loads((root/name).read_text(encoding='utf-8'))
    return read

def test_p401h_to_p402_contract(historical):
    edges=historical('p401h_top10_timeframe_balanced.json')
    routes=historical('p402_shadow_routes.json')
    assert len(edges)==len(routes)==10
    assert [e['job_id'] for e in edges]==[r['edge_id'] for r in routes]
    assert [e['institutional_score'] for e in edges]==[r['score'] for r in routes]

def test_p402_replay_matches_historical(historical):
    edges=historical('p401h_top10_timeframe_balanced.json')
    routes=historical('p402_shadow_routes.json')
    assert all(r['shadow_action']=='SHADOW_WATCH' for r in routes)
    assert route_shadow(edges,[])==routes

def test_p403_historical_ranking(historical):
    report=historical('p403_500_master_report.json')
    evidence={k:report[k] for k in ('LIVE','REAL_BROKER','REAL_ORDERS','FTMO_REAL','MT5_REAL')}
    evidence['POSITIONS_TOTAL']=report['POSITIONS_TOTAL']
    ranked=score_routes(historical('p402_shadow_routes.json'),evidence)
    assert len(ranked)==report['SHADOW_SIGNALS_SCORED']==10
    assert ranked[0]==report['TOP_SHADOW_SIGNAL']

def test_integrated_no_orders(historical):
    edges=historical('p401h_top10_timeframe_balanced.json')
    report=historical('p403_500_master_report.json')
    evidence={k:report[k] for k in ('LIVE','REAL_BROKER','REAL_ORDERS','FTMO_REAL','MT5_REAL')}
    evidence['POSITIONS_TOTAL']=0
    ranked=score_routes(route_shadow(edges,[]),evidence)
    assert all(r['order_sent'] is False and r['REAL_ORDERS']=='FORBIDDEN' and r['execution_mode']=='SHADOW_ONLY' for r in ranked)
