import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import run_p2071_2080

@pytest.mark.parametrize("cycles", [0, -1, True, 1.5, "100", None])
def test_invalid_cycles_rejected_before_artifacts(tmp_path, cycles):
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="INVALID_PAPER_RUNTIME_CYCLES"):
        run_p2071_2080("missing_portfolio.json", str(output), cycles=cycles)
    assert not output.exists()
