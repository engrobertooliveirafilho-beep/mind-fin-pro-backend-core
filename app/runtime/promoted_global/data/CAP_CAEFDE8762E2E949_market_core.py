import csv, sqlite3, json, math, statistics
from pathlib import Path
from datetime import datetime, UTC

SCHEMA = """
CREATE TABLE IF NOT EXISTS ohlcv (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 symbol TEXT NOT NULL,
 timeframe TEXT NOT NULL,
 ts TEXT NOT NULL,
 open REAL NOT NULL,
 high REAL NOT NULL,
 low REAL NOT NULL,
 close REAL NOT NULL,
 volume REAL NOT NULL,
 source_file TEXT NOT NULL,
 ingested_at TEXT NOT NULL,
 UNIQUE(symbol,timeframe,ts)
);
CREATE TABLE IF NOT EXISTS backtest_runs (
 id TEXT PRIMARY KEY,
 symbol TEXT,
 timeframe TEXT,
 strategy TEXT,
 params_json TEXT,
 started_at TEXT,
 report_json TEXT,
 decision TEXT
);
"""

def db(path="mind_trader/data/market.sqlite"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con=sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con

def ingest_ohlcv_csv(csv_path, symbol, timeframe, db_path="mind_trader/data/market.sqlite"):
    p=Path(csv_path)
    if not p.exists(): raise FileNotFoundError(str(p))
    con=db(db_path)
    rows=0
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        needed={"ts","open","high","low","close","volume"}
        if not needed.issubset(set(r.fieldnames or [])):
            raise ValueError(f"CSV precisa conter colunas: {sorted(needed)}")
        for x in r:
            con.execute("""INSERT OR IGNORE INTO ohlcv(symbol,timeframe,ts,open,high,low,close,volume,source_file,ingested_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",(symbol,timeframe,x["ts"],float(x["open"]),float(x["high"]),float(x["low"]),float(x["close"]),float(x["volume"]),str(p),datetime.now(UTC).isoformat()))
            rows+=1
    con.commit(); con.close()
    return {"ingested_rows_seen":rows,"db_path":db_path,"symbol":symbol,"timeframe":timeframe}

def load_ohlcv(symbol,timeframe,db_path="mind_trader/data/market.sqlite"):
    con=db(db_path)
    cur=con.execute("SELECT ts,open,high,low,close,volume FROM ohlcv WHERE symbol=? AND timeframe=? ORDER BY ts",(symbol,timeframe))
    data=[dict(ts=a,open=b,high=c,low=d,close=e,volume=f) for a,b,c,d,e,f in cur.fetchall()]
    con.close()
    return data

def sma(vals,n):
    return [None if i+1<n else sum(vals[i+1-n:i+1])/n for i in range(len(vals))]

def metrics(equity, trades):
    if not trades: return {"trades":0,"net_profit":0,"max_drawdown":0,"profit_factor":0,"expectancy":0,"win_rate":0}
    pnl=[t["pnl"] for t in trades]
    wins=[x for x in pnl if x>0]; losses=[x for x in pnl if x<0]
    peak=equity[0]; dd=0
    for v in equity:
        peak=max(peak,v); dd=max(dd,peak-v)
    pf=(sum(wins)/abs(sum(losses))) if losses else (999 if wins else 0)
    return {"trades":len(trades),"net_profit":sum(pnl),"max_drawdown":dd,"profit_factor":pf,"expectancy":statistics.mean(pnl),"win_rate":len(wins)/len(pnl)}

def backtest_sma_cross(symbol,timeframe,fast=9,slow=21,initial_capital=100000,cost_per_trade=1.0,slippage_points=0.0,db_path="mind_trader/data/market.sqlite"):
    data=load_ohlcv(symbol,timeframe,db_path)
    if len(data)<slow+10: raise ValueError("DADOS_INSUFICIENTES_REAIS")
    closes=[x["close"] for x in data]; f=sma(closes,fast); s=sma(closes,slow)
    cash=initial_capital; pos=0; entry=0; trades=[]; equity=[cash]
    for i in range(1,len(data)):
        if f[i-1] is None or s[i-1] is None: continue
        buy=f[i-1]<=s[i-1] and f[i]>s[i]
        sell=f[i-1]>=s[i-1] and f[i]<s[i]
        price=data[i]["close"]
        if buy and pos==0:
            pos=1; entry=price+slippage_points; cash-=cost_per_trade
        elif sell and pos==1:
            exitp=price-slippage_points; pnl=exitp-entry-cost_per_trade
            cash+=pnl; trades.append({"entry":entry,"exit":exitp,"pnl":pnl,"ts":data[i]["ts"]}); pos=0
        equity.append(cash + ((price-entry) if pos else 0))
    m=metrics(equity,trades)
    report={"symbol":symbol,"timeframe":timeframe,"strategy":"SMA_CROSS","params":{"fast":fast,"slow":slow,"cost_per_trade":cost_per_trade,"slippage_points":slippage_points},"metrics":m,"edge_claim":"NONE","decision":"RESEARCH_ONLY_NOT_PROMOTED"}
    return report

def walk_forward(symbol,timeframe,windows=3,db_path="mind_trader/data/market.sqlite"):
    data=load_ohlcv(symbol,timeframe,db_path)
    if len(data)<90: raise ValueError("WALK_FORWARD_REQUER_90_BARRAS_REAIS")
    chunk=len(data)//windows
    results=[]
    for w in range(windows):
        start=w*chunk; end=(w+1)*chunk if w<windows-1 else len(data)
        tmp=f"mind_trader/data/wf_{w}.sqlite"
        con=db(tmp)
        for x in data[start:end]:
            con.execute("INSERT OR IGNORE INTO ohlcv(symbol,timeframe,ts,open,high,low,close,volume,source_file,ingested_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(symbol,timeframe,x["ts"],x["open"],x["high"],x["low"],x["close"],x["volume"],"walk_forward_slice",datetime.now(UTC).isoformat()))
        con.commit(); con.close()
        try: results.append(backtest_sma_cross(symbol,timeframe,db_path=tmp))
        except Exception as e: results.append({"error":str(e)})
    stable=all(("metrics" in r and r["metrics"]["trades"]>0) for r in results)
    return {"windows":windows,"results":results,"stable":stable,"decision":"NOT_PROMOTED" if not stable else "CANDIDATE_REQUIRES_MORE_VALIDATION"}

def save_report(report,path="mind_trader/reports/P8.28_report.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
