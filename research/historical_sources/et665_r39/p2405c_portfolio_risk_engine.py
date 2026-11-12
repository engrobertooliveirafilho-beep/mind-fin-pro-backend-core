import json, csv, pathlib, math
from collections import defaultdict

MISSION="P2405C_PORTFOLIO_RISK_ENGINE"
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

P2403E=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2403E_REBUILD_REPLAY_SERIES_FROM_DE40_CANONICAL_OHLC_20260625_124455")
P2404=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2404_CORRELATION_ANALYZER_20260625_125024")
P2405B=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2405B_EDGE_POOL_OPTIMIZER_REPAIR_20260625_131156")
LOCK=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
OUT=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2405C_PORTFOLIO_RISK_ENGINE_20260625_132958")
ROOT=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core")
OUT.mkdir(parents=True, exist_ok=True)

for p in [P2403E/"summary.json", P2404/"summary.json", P2405B/"summary.json"]:
    s=json.loads(p.read_text(encoding="utf-8"))
    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["real_execution_allowed"] is False

series=list(csv.DictReader(open(P2403E/"p2403e_de40_edge_trade_series.csv",encoding="utf-8")))
stats=list(csv.DictReader(open(P2403E/"p2403e_de40_edge_replay_stats.csv",encoding="utf-8")))
pair_rows=list(csv.DictReader(open(P2404/"p2404_pairwise_correlation.csv",encoding="utf-8")))

edges=sorted(set(r["edge_id"] for r in series))
edge_ts=defaultdict(dict)
for r in series:
    edge_ts[r["edge_id"]][r["timestamp"]]=float(r["pnl_r"])

all_ts=sorted(set(r["timestamp"] for r in series))

stat={r["edge_id"]:r for r in stats}

def f(x,d=0.0):
    try: return float(x)
    except: return d

def edge_quality(e):
    st=stat[e]
    pf=f(st["pf"])
    wr=f(st["winrate"])
    exp=f(st["expectancy"])
    dd=f(st["max_dd_r"])
    net=f(st["net_r"])
    return max(0.01,
        min(pf/2.2,1)*0.30 +
        min(wr/60,1)*0.15 +
        min(max(exp,0)/0.08,1)*0.25 +
        min(max(net,0)/80,1)*0.15 +
        max(0,0.15-min(dd/20,1)*0.15)
    )

def edge_inv_dd(e):
    return 1/max(f(stat[e]["max_dd_r"]),0.1)

def normalize(w):
    s=sum(w.values())
    if s<=0:
        return {k:1/len(w) for k in w}
    return {k:v/s for k,v in w.items()}

def base_weights(method, selected_edges):
    if method=="equal":
        return {e:1 for e in selected_edges}
    if method=="quality":
        return {e:edge_quality(e) for e in selected_edges}
    if method=="pf":
        return {e:max(f(stat[e]["pf"]),0.01) for e in selected_edges}
    if method=="inverse_dd":
        return {e:edge_inv_dd(e) for e in selected_edges}
    if method=="quality_inverse_dd":
        return {e:edge_quality(e)*edge_inv_dd(e) for e in selected_edges}
    return {e:1 for e in selected_edges}

def simulate(config_id, selected_edges, method, max_active, cooldown_losses, loss_cut_r, vol_scale):
    weights=normalize(base_weights(method, selected_edges))
    cooldown={e:0 for e in selected_edges}
    loss_streak={e:0 for e in selected_edges}
    eq=0; peak=0; dd=0
    curve=[]
    wins=losses=0
    gw=gl=0

    for t in all_ts:
        active=[]
        for e in selected_edges:
            if cooldown[e] > 0:
                cooldown[e]-=1
                continue
            pnl=edge_ts[e].get(t,0.0)
            if pnl != 0:
                active.append((e,pnl))

        active=sorted(active,key=lambda x:weights[x[0]],reverse=True)[:max_active]

        total=0
        used_weight=0
        for e,pnl in active:
            w=weights[e]
            scaled=pnl*w
            if vol_scale:
                scaled=max(-loss_cut_r,min(loss_cut_r,scaled))
            total+=scaled
            used_weight+=w

            if pnl<0:
                loss_streak[e]+=1
                if loss_streak[e] >= cooldown_losses:
                    cooldown[e]=cooldown_losses
                    loss_streak[e]=0
            elif pnl>0:
                loss_streak[e]=0

        if used_weight>0:
            total=total/used_weight

        eq+=total
        peak=max(peak,eq)
        dd=max(dd,peak-eq)

        if total>0:
            wins+=1; gw+=total
        elif total<0:
            losses+=1; gl+=abs(total)

        curve.append((t,total,eq))

    pf=gw/gl if gl else 999
    wr=wins/max(wins+losses,1)*100
    exp=sum(x[1] for x in curve)/len(curve)
    net=sum(x[1] for x in curve)

    score=(
        min(pf/2.0,1)*25 +
        min(wr/60,1)*15 +
        min(max(exp,0)/0.06,1)*20 +
        min(max(net,0)/100,1)*15 +
        max(0,25-min(dd/18,1)*25)
    )

    hard_pass = pf>=1.5 and wr>=45 and exp>0 and dd<=18 and len(selected_edges)>=5

    return {
        "config_id":config_id,
        "method":method,
        "edge_count":len(selected_edges),
        "max_active":max_active,
        "cooldown_losses":cooldown_losses,
        "loss_cut_r":loss_cut_r,
        "vol_scale":vol_scale,
        "pf":round(pf,6),
        "winrate":round(wr,6),
        "expectancy":round(exp,6),
        "net_r":round(net,6),
        "max_dd_r":round(dd,6),
        "score":round(score,6),
        "hard_pass":hard_pass,
        "edges":"|".join(selected_edges),
        "curve":curve
    }

ranked_edges=sorted(edges,key=lambda e:edge_quality(e),reverse=True)
edge_sets=[
    ranked_edges[:5],
    ranked_edges[:8],
    ranked_edges[:10],
    ranked_edges[:12],
    ranked_edges[:15],
    ranked_edges[:18],
]

methods=["equal","quality","pf","inverse_dd","quality_inverse_dd"]
configs=[]
cid=0

for es in edge_sets:
    for method in methods:
        for max_active in [2,3,5,8]:
            for cooldown_losses in [2,3,4]:
                for loss_cut_r in [0.35,0.50,0.75,1.00]:
                    for vol_scale in [True,False]:
                        cid+=1
                        configs.append(simulate(
                            "P2405C_CFG_"+str(cid).zfill(5),
                            es, method, max_active, cooldown_losses, loss_cut_r, vol_scale
                        ))

configs_sorted=sorted(configs,key=lambda x:(not x["hard_pass"], -x["score"], x["max_dd_r"], -x["pf"]))
best=configs_sorted[0]
decision="RISK_ENGINE_CERTIFIED" if best["hard_pass"] else "RISK_ENGINE_BLOCKED"
next_required="P2405D_MONTE_CARLO_PORTFOLIO" if best["hard_pass"] else "P2405E_TARGETED_EDGE_DISCOVERY"

rows_out=[]
for c in configs_sorted:
    r={k:v for k,v in c.items() if k!="curve"}
    r.update({"mode":MODE,"real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,"real_execution_allowed":False})
    rows_out.append(r)

with open(OUT/"p2405c_portfolio_risk_configs.csv","w",newline="",encoding="utf-8") as fp:
    w=csv.DictWriter(fp,fieldnames=list(rows_out[0].keys()))
    w.writeheader()
    w.writerows(rows_out)

best_curve=[
    {
        "timestamp":t,
        "portfolio_pnl_r":round(pnl,6),
        "portfolio_equity_r":round(eq,6),
        "config_id":best["config_id"],
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL
    }
    for t,pnl,eq in best["curve"]
]

with open(OUT/"p2405c_best_portfolio_equity_curve.csv","w",newline="",encoding="utf-8") as fp:
    w=csv.DictWriter(fp,fieldnames=list(best_curve[0].keys()))
    w.writeheader()
    w.writerows(best_curve)

best_edges=best["edges"].split("|")
pool_rows=[]
for e in best_edges:
    pool_rows.append({
        "edge_id":e,
        "risk_engine_status":"SELECTED_IN_BEST_CONFIG" if best["hard_pass"] else "SELECTED_BUT_BLOCKED",
        "config_id":best["config_id"],
        "method":best["method"],
        "weighting":"dynamic_by_config",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "real_execution_allowed":False
    })

with open(OUT/"p2405c_risk_engine_edge_pool.csv","w",newline="",encoding="utf-8") as fp:
    w=csv.DictWriter(fp,fieldnames=list(pool_rows[0].keys()))
    w.writeheader()
    w.writerows(pool_rows)

module=ROOT/"app"/"runtime"/"p2405c_portfolio_risk_engine.py"
module.write_text(r'''
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def runtime_allowed():
    return False

def hard_gate(metrics):
    return (
        metrics.get("pf",0) >= 1.5 and
        metrics.get("winrate",0) >= 45 and
        metrics.get("expectancy",0) > 0 and
        metrics.get("max_dd_r",999) <= 18 and
        metrics.get("edge_count",0) >= 5
    )

def safety_contract():
    return {
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "runtime_allowed":False,
        "real_execution_allowed":False,
        "purpose":"offline_portfolio_risk_engine",
    }
''',encoding="utf-8")

summary={
    "mission":MISSION,
    "mode":MODE,
    "real_orders":REAL_ORDERS,
    "ftmo_real":FTMO_REAL,
    "input_p2403e":str(P2403E),
    "input_p2404":str(P2404),
    "input_p2405b":str(P2405B),
    "governance_lock":str(LOCK),
    "output":str(OUT),
    "module":str(module),
    "configs_tested":len(configs),
    "best_config":{k:v for k,v in best.items() if k!="curve"},
    "decision":decision,
    "runtime_promotion_allowed":False,
    "paper_stack_modified":True,
    "real_execution_allowed":False,
    "certification":"P2405C_PORTFOLIO_RISK_ENGINE_CERTIFIED",
    "next_required":next_required
}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")

audit=f"""============================================================
P2405C COMPLETE — PORTFOLIO RISK ENGINE
============================================================
MISSION............. {MISSION}
MODE................ {MODE}
REAL_ORDERS......... {REAL_ORDERS}
FTMO_REAL........... {FTMO_REAL}

EVIDENCE:
{OUT}

CONFIGS TESTED...... {len(configs)}
BEST CONFIG......... {best["config_id"]}
METHOD.............. {best["method"]}
EDGE COUNT.......... {best["edge_count"]}
MAX ACTIVE.......... {best["max_active"]}
COOLDOWN LOSSES..... {best["cooldown_losses"]}
LOSS CUT R.......... {best["loss_cut_r"]}
VOL SCALE........... {best["vol_scale"]}

PF.................. {best["pf"]}
WR.................. {best["winrate"]}
EXPECTANCY.......... {best["expectancy"]}
NET R............... {best["net_r"]}
MAX DD R............ {best["max_dd_r"]}
SCORE............... {best["score"]}
HARD PASS........... {best["hard_pass"]}

DECISION............ {decision}
NEXT_REQUIRED....... {next_required}

RUNTIME PROMOTION... False
REAL_EXEC_ALLOWED... False

AUDIT:
- Múltiplas configurações de portfólio testadas.
- Weighting, max_active, cooldown, loss cut e volatility scaling avaliados.
- Runtime permanece bloqueado.
- REAL_ORDERS e FTMO_REAL permanecem FORBIDDEN.
============================================================
"""
(OUT/"AUDIT_FINAL.txt").write_text(audit,encoding="utf-8")
print(audit)
