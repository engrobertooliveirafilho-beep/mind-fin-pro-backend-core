import pytest
from app.modules.hyper_context_builder import HyperContextBuilder

def test_layers():
    b=HyperContextBuilder(); b.add_layer('a', {'x':1}); b.add_layer('b', {'y':2})
    assert b.build()=={'a':{'x':1},'b':{'y':2}}

def test_duplicate():
    b=HyperContextBuilder(); b.add_layer('a', {})
    with pytest.raises(ValueError): b.add_layer('a', {'x':1})
    assert b.build()=={'a':{}}

def test_isolation():
    b=HyperContextBuilder(); d={'x':[1]}; b.add_layer('a',d); d['x'].append(2); b.build()['a']['x'].append(3)
    assert b.build()=={'a':{'x':[1]}}
