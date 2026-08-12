import json, time
from pathlib import Path
from mind_trader.app.backtest.market_core import backtest_sma_cross, load_ohlcv, metrics
from mind_trader.app.validation.edge_validation import validate_backtest_trades
from mind_trader.app.genomes.strategy_genome import validate_genome
from mind_trader.app.data.dataset_lineage_gate import require_dataset_with_lineage

def backtest_breakout(symbol,timeframe,lookback=20,buffer=0.0,initial_capital=100000,cost_per_trade=1.0,db_path="mind_trader/data/market.sqlite"):
    rows=load_ohlcv(symbol,timeframe,db_path)
    if len(rows)<lookback+10: raise ValueError("DADOS_INSUFICIENTES_REAIS")
    cash=initial_capital; pos=0; entry=0; trades=[]; equity=[cash]
    for i in range(lookback,len(rows)):
        prev_high=max(float(r["high"]) for r in rows[i-lookback:i])
        prev_low=min(float(r["low"]) for r in rows[i-lookback:i])
        price=float(rows[i]["close"])
        if pos==0 and price>prev_high+buffer:
            pos=1; entry=price; cash-=cost_per_trade
        elif pos==1 and price<prev_low:
            pnl=price-entry-cost_per_trade; cash+=pnl; trades.append({"entry":entry,"exit":price,"pnl":pnl,"ts":rows[i]["ts"]}); pos=0
        equity.append(cash+((price-entry) if pos else 0))
    return {"symbol":symbol,"timeframe":timeframe,"strategy":"BREAKOUT","params":{"lookback":lookback,"buffer":buffer},"metrics":metrics(equity,trades),"trades":trades,"decision":"RESEARCH_ONLY_NOT_PROMOTED","production":"BLOCKED","edge_claim":"NONE"}

def backtest_pullback(symbol,timeframe,ema=20,pullback_depth=0.5,initial_capital=100000,cost_per_trade=1.0,db_path="mind_trader/data/market.sqlite"):
    rows=load_ohlcv(symbol,timeframe,db_path)
    if len(rows)<ema+10: raise ValueError("DADOS_INSUFICIENTES_REAIS")
    closes=[float(r["close"]) for r in rows]
    alpha=2/(ema+1); e=[]; cur=closes[0]
    for c in closes:
        cur=alpha*c+(1-alpha)*cur; e.append(cur)
    cash=initial_capital; pos=0; entry=0; trades=[]; equity=[cash]
    for i in range(ema,len(rows)):
        price=closes[i]
        trend=e[i]>e[i-5] if i>=5 else False
        dip=(e[i]-price)/e[i] if e[i] else 0
        if pos==0 and trend and dip>pullback_depth/100:
            pos=1; entry=price; cash-=cost_per_trade
        elif pos==1 and (price>e[i] or not trend):
            pnl=price-entry-cost_per_trade; cash+=pnl; trades.append({"entry":entry,"exit":price,"pnl":pnl,"ts":rows[i]["ts"]}); pos=0
        equity.append(cash+((price-entry) if pos else 0))
    return {"symbol":symbol,"timeframe":timeframe,"strategy":"PULLBACK","params":{"ema":ema,"pullback_depth":pullback_depth},"metrics":metrics(equity,trades),"trades":trades,"decision":"RESEARCH_ONLY_NOT_PROMOTED","production":"BLOCKED","edge_claim":"NONE"}

def synthetic_trades_from_backtest(report):
    trades=report.get("trades")
    if trades is not None: return trades
    m=report.get("metrics",{}); n=int(m.get("trades",0)); exp=float(m.get("expectancy",0))
    return [{"pnl":exp} for _ in range(n)]

def run_genome_backtest(genome, db_path="mind_trader/data/market.sqlite", dataset_id=None, catalog_path="mind_trader/reports/P8.61_data_catalog.json", lineage_path="mind_trader/reports/P8.64_dataset_lineage.json"):
    if dataset_id:
        ds=require_dataset_with_lineage(dataset_id,catalog_path,lineage_path)
        if not ds["allowed"]:
            return {"genome_id":genome.get("genome_id"),"status":"BLOCKED_DATASET_LINEAGE","dataset_lineage_check":ds,"production":"BLOCKED","edge_claim":"NONE"}

    ok,reason=validate_genome(genome)
    if not ok:
        return {"genome_id":genome.get("genome_id"),"status":"BLOCKED","reason":reason,"production":"BLOCKED","edge_claim":"NONE"}

    p=genome["params"]
    try:
        if genome["strategy_type"]=="SMA_CROSS":
            bt=backtest_sma_cross(genome["symbol"],genome["timeframe"],fast=p["fast"],slow=p["slow"],db_path=db_path)
        elif genome["strategy_type"]=="BREAKOUT":
            bt=backtest_breakout(genome["symbol"],genome["timeframe"],lookback=p["lookback"],buffer=p["buffer"],db_path=db_path)
        elif genome["strategy_type"]=="PULLBACK":
            bt=backtest_pullback(genome["symbol"],genome["timeframe"],ema=p["ema"],pullback_depth=p["pullback_depth"],db_path=db_path)
        else:
            return {"genome_id":genome["genome_id"],"status":"SKIPPED_UNSUPPORTED_STRATEGY","production":"BLOCKED","edge_claim":"NONE"}

        validation=validate_backtest_trades(synthetic_trades_from_backtest(bt))
        return {"genome_id":genome["genome_id"],"status":"TESTED","dataset_id":dataset_id,"backtest":bt,"validation":validation,"production":"BLOCKED","edge_claim":"NONE"}
    except Exception as e:
        return {"genome_id":genome["genome_id"],"status":"FAILED","reason":str(e),"production":"BLOCKED","edge_claim":"NONE"}

def massive_backtest_cluster(genomes, db_path="mind_trader/data/market.sqlite", limit=None, dataset_id=None, catalog_path="mind_trader/reports/P8.61_data_catalog.json", lineage_path="mind_trader/reports/P8.64_dataset_lineage.json"):
    started=time.time(); selected=genomes[:limit] if limit else genomes
    results=[run_genome_backtest(g,db_path,dataset_id,catalog_path,lineage_path) for g in selected]
    ranked=sorted(results,key=lambda r: float(r.get("backtest",{}).get("metrics",{}).get("expectancy",0)),reverse=True)
    return {"requested":len(genomes),"executed":len(selected),"tested":sum(1 for r in results if r["status"]=="TESTED"),"failed":sum(1 for r in results if r["status"]=="FAILED"),"skipped":sum(1 for r in results if r["status"].startswith("SKIPPED")),"blocked":sum(1 for r in results if r["status"].startswith("BLOCKED")),"elapsed_sec":round(time.time()-started,6),"ranking":ranked,"decision":"RESEARCH_ONLY","production":"BLOCKED","edge_claim":"NONE"}

def save_cluster_report(report,path="mind_trader/reports/P8.37_massive_backtest_cluster.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
