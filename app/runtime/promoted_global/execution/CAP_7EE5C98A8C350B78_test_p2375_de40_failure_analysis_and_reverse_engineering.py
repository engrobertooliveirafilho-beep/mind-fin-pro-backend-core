from app.runtime.p2375_de40_failure_analysis_and_reverse_engineering import aggregate, reverse_engineer_failures


def test_aggregate_by_family():
    rows = [
        {"family": "A", "expectancy_r": "0.1", "profit_factor": "1.2", "trades": "10"},
        {"family": "A", "expectancy_r": "-0.1", "profit_factor": "0.8", "trades": "20"},
        {"family": "B", "expectancy_r": "0.2", "profit_factor": "1.5", "trades": "30"},
    ]
    out = aggregate(rows, ["family"])
    assert len(out) == 2
    assert out[0]["family"] == "B"


def test_reverse_engineering_flags_failure():
    wf = [{
        "family": "PULLBACK",
        "variant": "EMA_PULLBACK",
        "profile": "INTRADAY",
        "timeframe": "M5",
        "train_expectancy_r": "0.1",
        "validation_expectancy_r": "-0.1",
        "test_expectancy_r": "-0.2",
        "train_pf": "1.5",
        "test_pf": "0.7",
        "test_trades": "30",
    }]
    out = reverse_engineer_failures([], wf)
    assert "TEST_FAILED" in out[0]["failure_mode"]
    assert "PF_COLLAPSE_OUT_OF_SAMPLE" in out[0]["failure_mode"]
