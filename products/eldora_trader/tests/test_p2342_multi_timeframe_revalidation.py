from app.runtime.p2342_multi_timeframe_revalidation import evaluate

def test_revalidation():
    r=evaluate("EURUSD","BUY",{
        "m1":True,
        "m5":True,
        "m15":True,
        "h1":True,
        "trend_filter":True,
        "volatility_filter":True,
        "session_filter":True,
        "support_resistance_filter":True
    })
    assert r.approved()
