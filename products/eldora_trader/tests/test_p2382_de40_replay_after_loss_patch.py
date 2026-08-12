from app.runtime.p2382_de40_replay_after_loss_patch import classify, aggregate, max_dd


def test_classify_promotes_good_row():
    row = {
        "realized_r": "1.0",
        "profit_factor_proxy": "1.8",
        "expectancy_r_proxy": "0.2",
    }
    assert classify(row) == "PROMOTE_AFTER_PATCH_REPLAY"


def test_aggregate_promotes_group():
    rows = []
    for _ in range(25):
        rows.append({
            "family": "PULLBACK",
            "timeframe": "M5",
            "realized_r": "1",
            "mae_r": "0.5",
            "mfe_r": "2.5",
        })
    out = aggregate(rows, ["family", "timeframe"])
    assert out[0]["decision"] == "PROMOTE_GROUP_AFTER_PATCH"


def test_max_dd_basic():
    assert max_dd([1, -2, 1]) == 2
