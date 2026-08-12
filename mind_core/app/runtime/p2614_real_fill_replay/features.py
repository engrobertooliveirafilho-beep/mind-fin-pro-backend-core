import statistics

def build_features(candles):
    out={}
    for i,c in enumerate(candles):
        if i<60:
            continue
        prev=candles[i-1]
        w14=candles[i-14:i]
        w50=candles[i-50:i]
        w200=candles[max(0,i-200):i]
        atr=sum(x["high"]-x["low"] for x in w14)/14
        atr_med=statistics.median([x["high"]-x["low"] for x in w200]) if w200 else atr
        sma14=sum(x["close"] for x in w14)/14
        sma50=sum(x["close"] for x in w50)/50
        body=abs(c["close"]-c["open"])
        rng=max(c["high"]-c["low"],0.0001)
        hour=c["time"].hour
        session="EU_MORNING" if 7<=hour<11 else "EU_AFTERNOON" if 11<=hour<14 else "US_MORNING" if 14<=hour<17 else "US_AFTERNOON" if 17<=hour<21 else "ASIA"
        out[i]={
            "idx":i,
            "time":c["time"],
            "atr":atr,
            "atr_med":atr_med,
            "trend":"TREND_UP" if sma14>sma50 else "TREND_DOWN",
            "regime":"HIGH_VOL" if atr>atr_med else "LOW_VOL",
            "session":session,
            "body_ratio":body/rng,
            "wick_ratio":(rng-body)/rng,
            "ret":(c["close"]-prev["close"])/prev["close"]
        }
    return out
