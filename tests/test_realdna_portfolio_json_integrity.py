import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio

@pytest.mark.parametrize("payload", [
    '{"specialists":[{"id":"A","id":"B","logic_type":"RANGE_REVERSION"}]}',
    '{"specialists":[{"id":"A","logic_type":"RANGE_REVERSION","weight":NaN}]}',
    '{"specialists":[{"id":"A","logic_type":"RANGE_REVERSION","weight":Infinity}]}',
    '{"specialists":[{"id":"A","logic_type":"RANGE_REVERSION","weight":-Infinity}]}',
])
def test_ambiguous_or_nonfinite_realdna_payload_rejected(tmp_path, payload):
    portfolio = tmp_path / "portfolio.json"
    portfolio.write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError, match="DUPLICATE_REALDNA_PORTFOLIO_KEY|NONFINITE_REALDNA_PORTFOLIO"):
        load_portfolio(str(portfolio))

def test_valid_minimal_realdna_schema_accepted(tmp_path):
    portfolio = tmp_path / "portfolio.json"
    portfolio.write_text('{"specialists":[{"id":"A","logic_type":"RANGE_REVERSION"}]}', encoding="utf-8")
    assert load_portfolio(str(portfolio))[0]["id"] == "A"
