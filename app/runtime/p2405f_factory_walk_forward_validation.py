"""P2405: simultaneous PAPER portfolio replay and chronological walk-forward."""
from datetime import datetime,timedelta
from math import floor

MODE="PAPER_ONLY"; REAL_ORDERS="FORBIDDEN"; FTMO_REAL="FORBIDDEN"

def _dt(x): return datetime.fromisoformat(str(x).replace("Z","+00:00"))
def _pf(rs):
    wins=sum(x for x in rs if x>0); losses=-sum(x for x in rs if x<0)
    return wins/losses if losses>0 else (float("inf") if wins>0 else 0.0)
def _metrics(rows):
    rs=[float(r["net_pnl_per_lot"])/float(r["risk_per_lot"]) for r in rows]
    return {"trades":len(rs),"pf":_pf(rs),"expectancy_r":sum(rs)/len(rs) if rs else 0.0,
            "net_r":sum(rs),"win_rate_pct":100*sum(x>0 for x in rs)/len(rs) if rs else 0.0}

def replay_portfolio(trades,initial_equity=10000.0,risk_per_trade=.0025,max_open_risk=.02):
    if initial_equity<=0 or not 0<risk_per_trade<=max_open_risk<=1: raise ValueError("Invalid equity/risk limits")
    timeline={}
    for i,t in enumerate(trades):
        if t.get("mode")!="PAPER_ONLY" or t.get("real_orders")!="FORBIDDEN" or t.get("ftmo_real")!="FORBIDDEN" or t.get("real_execution_allowed") is not False:
            raise ValueError("Safety contract failed")
        if float(t["risk_per_lot"])<=0 or float(t["volume_step"])<=0: raise ValueError("Invalid risk/volume step")
        en,ex=_dt(t["entry_time"]),_dt(t["exit_time"])
        if ex<=en: raise ValueError("Invalid trade interval")
        timeline.setdefault(en,{"entries":[],"exits":[]})["entries"].append((i,t))
        timeline.setdefault(ex,{"entries":[],"exits":[]})["exits"].append((i,t))
    equity=peak=initial_equity; max_dd=0.0; active={}; ledger=[]; rejected=[]
    peak_active=0; max_open_fraction=0.0
    for ts in sorted(timeline):
        batch=timeline[ts]
        for i,t in sorted(batch["exits"],key=lambda z:z[0]):
            pos=active.pop(i,None)
            if pos is None: continue
            pnl=float(t["net_pnl_per_lot"])*pos["lots"]
            equity+=pnl; peak=max(peak,equity); max_dd=max(max_dd,(peak-equity)/peak if peak else 0.0)
            ledger.append({"edge_id":t["edge_id"],"entry_time":pos["entry_time"],"exit_time":ts.isoformat(),
                "lots":pos["lots"],"risk_cash":pos["risk_cash"],"pnl_cash":pnl,"equity_after":equity,
                "mode":MODE,"real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL})
        entries=sorted(batch["entries"],key=lambda z:(str(z[1]["edge_id"]),z[0]))
        if entries:
            used=sum(p["risk_cash"] for p in active.values()); capacity=max(0.0,equity*max_open_risk-used)
            desired=equity*risk_per_trade*len(entries); scale=min(1.0,capacity/desired) if desired else 0.0
            for i,t in entries:
                risk_cash=equity*risk_per_trade*scale; step=float(t["volume_step"])
                lots=floor((risk_cash/float(t["risk_per_lot"])+1e-12)/step)*step
                lots=min(lots,float(t["volume_max"]))
                if lots+1e-12<float(t["volume_min"]):
                    rejected.append({"edge_id":t["edge_id"],"entry_time":ts.isoformat(),"reason":"BELOW_MIN_VOLUME"}); continue
                risk_cash=lots*float(t["risk_per_lot"])
                active[i]={"lots":lots,"risk_cash":risk_cash,"entry_time":ts.isoformat()}
                peak_active=max(peak_active,len(active))
                max_open_fraction=max(max_open_fraction,sum(p["risk_cash"] for p in active.values())/equity if equity else 0.0)
    if active: raise ValueError("Unclosed positions remain at end of replay")
    return {"equity_start":initial_equity,"equity_end":equity,"max_realized_drawdown_pct":max_dd*100,
        "closed_trades":len(ledger),"rejected_entries":len(rejected),"max_concurrent_positions":peak_active,
        "max_open_risk_fraction_observed":max_open_fraction},ledger,rejected

def walk_forward(trades,folds=3,train_fraction=.5,min_train_trades=30,min_pf=1.05,top_n=6,embargo_minutes=165):
    if folds<2 or not 0<train_fraction<1: raise ValueError("Invalid walk-forward configuration")
    ordered=sorted(trades,key=lambda t:_dt(t["entry_time"])); times=sorted({_dt(t["entry_time"]) for t in ordered})
    if len(times)<folds+2: raise ValueError("Insufficient chronological observations")
    results=[]
    for k in range(folds):
        train_cut=int(len(times)*(train_fraction+(1-train_fraction)*k/folds))
        test_cut=int(len(times)*(train_fraction+(1-train_fraction)*(k+1)/folds))
        split=times[min(train_cut,len(times)-1)]
        test_end=max(_dt(t["exit_time"]) for t in ordered) if k==folds-1 else times[min(max(test_cut,train_cut+1),len(times)-1)]
        embargo=timedelta(minutes=embargo_minutes)
        train=[t for t in ordered if _dt(t["exit_time"])<split-embargo]
        test=[t for t in ordered if _dt(t["entry_time"])>=split+embargo and _dt(t["exit_time"])<=test_end]
        per_edge={}
        for t in train: per_edge.setdefault(t["edge_id"],[]).append(t)
        ranked=[]
        for eid,rows in per_edge.items():
            m=_metrics(rows)
            if m["trades"]>=min_train_trades and m["expectancy_r"]>0 and m["pf"]>=min_pf: ranked.append((eid,m))
        selected=[eid for eid,m in sorted(ranked,key=lambda z:(z[1]["pf"],z[1]["expectancy_r"],z[1]["trades"]),reverse=True)[:top_n]]
        oos=[t for t in test if t["edge_id"] in set(selected)]
        if oos: portfolio,ledger,rejected=replay_portfolio(oos)
        else:
            portfolio={"equity_start":10000.0,"equity_end":10000.0,"max_realized_drawdown_pct":0.0,
                "closed_trades":0,"rejected_entries":0,"max_concurrent_positions":0,"max_open_risk_fraction_observed":0.0}
            ledger=[]; rejected=[]
        results.append({"fold":k+1,"train_end":split.isoformat(),"test_end":test_end.isoformat(),
            "embargo_minutes":embargo_minutes,"train_events":len(train),"test_events":len(oos),
            "selected_edges":selected,"oos_metrics":_metrics(oos),"portfolio":portfolio,
            "oos_ledger":ledger,"rejected_entries":rejected})
    return results

def safety_contract():
    return {"mode":MODE,"real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,
            "runtime_allowed":False,"real_execution_allowed":False}
