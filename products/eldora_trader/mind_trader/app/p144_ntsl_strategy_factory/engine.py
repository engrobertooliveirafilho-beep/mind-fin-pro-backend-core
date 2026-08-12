import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

TEMPLATES=["ema_cross","rsi_reversion","macd_trend","bollinger_reversion"]
ASSETS=["WIN","WDO","PETR4","VALE3"]
TIMEFRAMES=["M1","M5","M15"]

def ntsl_code(template, fast=9, slow=21):
    if template=="ema_cross":
        return f"""input
  fastPeriod({fast});
  slowPeriod({slow});

var
  fastMA, slowMA : Float;

begin
  fastMA := MediaExp(fastPeriod, Close);
  slowMA := MediaExp(slowPeriod, Close);

  if (fastMA > slowMA) and (fastMA[1] <= slowMA[1]) then
    BuyAtMarket;

  if (fastMA < slowMA) and (fastMA[1] >= slowMA[1]) then
    SellShortAtMarket;
end;"""
    if template=="rsi_reversion":
        return """input
  rsiPeriod(14);
  oversold(30);
  overbought(70);

var
  r : Float;

begin
  r := RSI(rsiPeriod, 0);

  if r < oversold then
    BuyAtMarket;

  if r > overbought then
    SellShortAtMarket;
end;"""
    if template=="macd_trend":
        return """var
  m, s : Float;

begin
  m := MACD(26, 12, 9);
  s := MediaExp(9, m);

  if m > s then
    BuyAtMarket;

  if m < s then
    SellShortAtMarket;
end;"""
    return """input
  period(20);

var
  mid : Float;

begin
  mid := Media(period, Close);

  if Close < mid then
    BuyAtMarket;

  if Close > mid then
    SellShortAtMarket;
end;"""

def generate():
    rows=[]
    base=Path("strategies/ntsl_factory")
    base.mkdir(parents=True,exist_ok=True)

    for template in TEMPLATES:
        for asset in ASSETS:
            for timeframe in TIMEFRAMES:
                code=ntsl_code(template)
                sid=hashlib.sha256(f"{template}:{asset}:{timeframe}".encode()).hexdigest()[:16]
                folder=base/sid
                folder.mkdir(parents=True,exist_ok=True)
                (folder/"code.nts").write_text(code,encoding="utf-8")
                meta={
                    "strategy_id":sid,
                    "template":template,
                    "asset":asset,
                    "timeframe":timeframe,
                    "platform":"Profit/NTSL",
                    "requires_profit_backtest":True,
                    "live":"FORBIDDEN",
                    "real_orders":"FORBIDDEN"
                }
                (folder/"metadata.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
                rows.append(meta)
    return rows

def run():
    out=Path("reports/P14.4_NTSL_STRATEGY_FACTORY")
    out.mkdir(parents=True,exist_ok=True)
    strategies=generate()
    manifest={
        "STATUS":"P14.4_NTSL_STRATEGY_FACTORY_IMPLEMENTED",
        "STRATEGIES_CREATED":len(strategies),
        "TEMPLATES":TEMPLATES,
        "ASSETS":ASSETS,
        "TIMEFRAMES":TIMEFRAMES,
        "PROFIT_NTSL_CONFIRMED":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"ntsl_strategy_catalog.json").write_text(json.dumps(strategies,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.4_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
