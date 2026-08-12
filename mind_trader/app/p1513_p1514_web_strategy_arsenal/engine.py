import json
from pathlib import Path
from datetime import datetime,UTC

FAMILIES={
 "trend_following":["sma_cross","ema_cross","adx_trend","donchian_trend"],
 "mean_reversion":["rsi_reversion","bollinger_reversion","vwap_reversion"],
 "breakout":["range_breakout","opening_range_breakout","volatility_breakout"],
 "volatility":["atr_expansion","bollinger_squeeze"],
 "volume":["volume_spike","obv_confirmation"],
 "market_regime":["trend_regime","sideways_regime","volatility_regime"],
 "multi_timeframe":["h1_trend_m15_entry","d1_bias_h1_entry"],
 "risk_management":["atr_stop","fixed_stop_take","trailing_stop"]
}

ASSETS=["WINFUT","WDOFUT","IBOV","PETR4","VALE3","IFIX","CSAN3"]

def web_registry():
    rows=[]
    for fam,patterns in FAMILIES.items():
        for p in patterns:
            rows.append({
                "source_type":"WEB_RESEARCH_HYPOTHESIS",
                "family":fam,
                "pattern":p,
                "trust_level":"LOW_UNTIL_BACKTESTED",
                "requires_backtest":True,
                "requires_walk_forward":True,
                "requires_monte_carlo":True,
                "live":"FORBIDDEN",
                "real_orders":"FORBIDDEN"
            })
    return rows

def arsenal():
    reg=web_registry()
    out=[]
    for asset in ASSETS:
        for r in reg:
            out.append({
                "asset":asset,
                "family":r["family"],
                "pattern":r["pattern"],
                "status":"HYPOTHESIS_ONLY",
                "promotion_required":"P15_BACKTEST_WF_MC_AUTHORITY",
                "live":"FORBIDDEN",
                "real_orders":"FORBIDDEN"
            })
    return out

def run():
    out=Path("reports/P15.13_P15.14_WEB_STRATEGY_ARSENAL")
    out.mkdir(parents=True,exist_ok=True)
    registry=web_registry()
    armory=arsenal()
    manifest={
        "STATUS":"P15.13_P15.14_WEB_STRATEGY_ARSENAL_IMPLEMENTED",
        "WEB_LEARNING":"ENABLED_AS_RESEARCH_ONLY",
        "STRATEGY_FAMILIES":len(FAMILIES),
        "WEB_HYPOTHESES":len(registry),
        "ARSENAL_HYPOTHESES":len(armory),
        "ASSETS":ASSETS,
        "EDGE":"NOT_PROVEN_FOR_WEB_STRATEGIES",
        "CAUSALITY":"NOT_PROVEN",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "NEXT":"P15.15_WEB_RESEARCH_TO_BACKTEST_QUEUE",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"web_strategy_registry.json").write_text(json.dumps(registry,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"asset_strategy_arsenal.json").write_text(json.dumps(armory,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P15.13_P15.14_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
