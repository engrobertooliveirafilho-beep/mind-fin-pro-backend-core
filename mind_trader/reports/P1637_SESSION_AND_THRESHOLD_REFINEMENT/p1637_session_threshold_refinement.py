import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

CONF = Path("reports/P1620_CONFLUENCE_ENGINE/confluence_snapshot.json")
OPPS = Path("reports/P1623_OPPORTUNITY_RANKING_ENGINE/opportunity_ranking.json")
OUT = Path("reports/P1637_SESSION_AND_THRESHOLD_REFINEMENT")
REPORT = OUT / "p1637_session_threshold_report.json"

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

conf = load(CONF)
opps = load(OPPS)

def session_from_hour(h):
    h = int(h)
    if 0 <= h <= 6:
        return "ASIA"
    if 7 <= h <= 9:
        return "LONDON_OPEN"
    if 10 <= h <= 12:
        return "LONDON"
    if 13 <= h <= 16:
        return "LONDON_NY_OVERLAP"
    if 17 <= h <= 20:
        return "NEW_YORK"
    return "POST_NY"

session_stats = defaultdict(lambda: {
    "samples":0,
    "avg_confluence":0,
    "max_confluence":0,
    "assets":defaultdict(int),
    "timeframes":defaultdict(int)
})

for c in conf:
    h = c.get("hour",0)
    s = session_from_hour(h)
    score = float(c.get("confluence_score") or 0)

    session_stats[s]["samples"] += 1
    session_stats[s]["avg_confluence"] += score
    session_stats[s]["max_confluence"] = max(session_stats[s]["max_confluence"], score)
    session_stats[s]["assets"][c.get("asset")] += 1
    session_stats[s]["timeframes"][c.get("timeframe")] += 1

session_library = []
for s,d in session_stats.items():
    n = max(d["samples"],1)
    session_library.append({
        "session":s,
        "samples":d["samples"],
        "avg_confluence":round(d["avg_confluence"]/n,6),
        "max_confluence":d["max_confluence"],
        "assets":dict(d["assets"]),
        "timeframes":dict(d["timeframes"]),
        "status":"SESSION_REFINED"
    })

refined_opps = []
for o in opps:
    h = int(o.get("hour") or 0)
    session = session_from_hour(h)

    deployment = float(o.get("deployment_score") or 0)
    confluence = float(o.get("confluence_score") or 0)

    session_bonus = 0
    if session in ["LONDON_OPEN","LONDON_NY_OVERLAP","NEW_YORK"]:
        session_bonus = 7
    elif session == "LONDON":
        session_bonus = 4

    refined_score = min(100, deployment*0.45 + confluence*0.45 + session_bonus)

    if refined_score >= 90:
        decision = "ELITE_CANDIDATE"
    elif refined_score >= 80:
        decision = "DEMO_CANDIDATE"
    elif refined_score >= 70:
        decision = "WATCH_HIGH_PRIORITY"
    else:
        decision = "WATCH_ONLY"

    refined_opps.append({
        **o,
        "refined_session":session,
        "session_bonus":session_bonus,
        "refined_opportunity_score":round(refined_score,6),
        "refined_decision":decision,
        "ORDER_SENT":False,
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN"
    })

refined_opps = sorted(refined_opps, key=lambda x:x["refined_opportunity_score"], reverse=True)

report = {
    "STATUS":"P1637_SESSION_AND_THRESHOLD_REFINEMENT_COMPLETED",
    "SESSIONS_REGISTERED":len(session_library),
    "OPPORTUNITIES_REFINED":len(refined_opps),
    "ELITE_CANDIDATES":len([x for x in refined_opps if x["refined_decision"]=="ELITE_CANDIDATE"]),
    "DEMO_CANDIDATES":len([x for x in refined_opps if x["refined_decision"]=="DEMO_CANDIDATE"]),
    "WATCH_HIGH_PRIORITY":len([x for x in refined_opps if x["refined_decision"]=="WATCH_HIGH_PRIORITY"]),
    "TOP10_REFINED":refined_opps[:10],
    "NEXT":"P1638_ADD_REFINED_SCORE_TO_MASTER_BRAIN",
    "ORDER_SENT":False,
    "REAL_ORDERS":"FORBIDDEN",
    "FTMO_REAL":"FORBIDDEN",
    "MT5_REAL":"FORBIDDEN",
    "generated_at":datetime.now(UTC).isoformat()
}

(OUT/"refined_session_library.json").write_text(json.dumps(session_library,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT/"refined_opportunity_ranking.json").write_text(json.dumps(refined_opps,indent=2,ensure_ascii=False),encoding="utf-8")
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(report,indent=2,ensure_ascii=False))
