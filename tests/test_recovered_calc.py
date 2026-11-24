import pytest
from app.tools.calc import tool_calc
from app.tools.registry import get_tool, register_tool

def test_arithmetic():
    assert get_tool('calc')('2+2*5') == {'ok': True, 'result': 12.0}

@pytest.mark.parametrize('expr', ['().__class__', '2**1000000', '1/0', '1e999', 'True', '1+'*300])
def test_rejection(expr):
    assert not tool_calc(expr)['ok']

def test_duplicate():
    with pytest.raises(ValueError):
        register_tool('calc')(lambda: None)
