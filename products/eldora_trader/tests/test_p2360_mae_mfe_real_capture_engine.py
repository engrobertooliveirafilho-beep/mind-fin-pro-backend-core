from app.runtime.p2360_mae_mfe_real_capture_engine import calculate_mae_mfe, health

def test_buy_mae_mfe():
    out = calculate_mae_mfe(
        {"symbol":"EURUSD","side":"BUY","entry_price":1.1000,"exit_price":1.1020},
        [1.0990,1.1010,1.1040,1.1020]
    )
    assert out["mae"] == -0.001
    assert out["mfe"] == 0.004
    assert out["exit_efficiency"] == 0.5

def test_sell_mae_mfe():
    out = calculate_mae_mfe(
        {"symbol":"EURUSD","side":"SELL","entry_price":1.1000,"exit_price":1.0980},
        [1.1010,1.0990,1.0960,1.0980]
    )
    assert out["mae"] == -0.001
    assert out["mfe"] == 0.004
    assert out["exit_efficiency"] == 0.5

def test_profit_available_not_captured():
    out = calculate_mae_mfe(
        {"symbol":"EURUSD","side":"BUY","entry_price":1.1000,"exit_price":1.0990},
        [1.1005,1.1030,1.0990]
    )
    assert out["lesson"] == "PROFIT_WAS_AVAILABLE_BUT_NOT_CAPTURED"

def test_health():
    assert health()["status"] == "OK"
