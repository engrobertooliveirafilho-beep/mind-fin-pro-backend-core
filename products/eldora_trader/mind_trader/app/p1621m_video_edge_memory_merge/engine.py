import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

P16=Path("reports/P16_AUTONOMOUS_RESEARCH_RUNTIME/p16_edge_memory.json")
VIDEO=Path("reports/P16.21L_VIDEO_STRATEGY_WF_MC/p1621l_approved_video_edges.json")
OUT=Path("reports/P16.21M_VIDEO_EDGE_MEMORY_MERGE")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def edge_key(e):
    raw="|".join([str(e.get("edge_id","")),str(e.get("dataset","")),str(e.get("normalized_strategy_id","")),str(e.get("normalized_family",""))])
    return hashlib.sha256(raw.encode()).hexdigest()[:24]

def normalize_video_edge(e):
    m=e.get("backtest_metrics",{})
    return {
        "edge_id":"VIDEO_"+edge_key(e),
        "source":"YOUTUBE_GOOGLE_VIDEO_ABSORPTION",
        "dataset":e.get("dataset"),
        "strategy_family":e.get("normalized_family"),
        "asset":e.get("normalized_asset"),
        "timeframe":e.get("normalized_timeframe"),
        "profit_factor":m.get("profit_factor"),
        "trades":m.get("trades"),
        "total_return":m.get("total_return"),
        "max_drawdown":m.get("max_drawdown"),
        "winrate":m.get("winrate"),
        "walk_forward_status":e.get("walk_forward_status"),
        "monte_carlo_status":e.get("monte_carlo_status"),
        "certification_status":"PAPER_RESEARCH_CERTIFIED",
        "created_at":datetime.now(UTC).isoformat(),
        **BLOCKS
    }

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    base=load(P16)
    video=[normalize_video_edge(x) for x in load(VIDEO)]
    merged={}
    for e in base+video:
        merged[e.get("edge_id")]=e
    merged_list=list(merged.values())
    report={
        "STATUS":"P16.21M_VIDEO_EDGE_MEMORY_MERGE_IMPLEMENTED",
        "BASE_EDGES":len(base),
        "VIDEO_EDGES_APPROVED":len(video),
        "MERGED_EDGE_MEMORY":len(merged_list),
        "CERTIFICATION":"PAPER_RESEARCH_CERTIFIED",
        "NEXT":"P16.21N_CONTINUOUS_YOUTUBE_LOOP_SCHEDULER",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621m_video_edges_normalized.json").write_text(json.dumps(video,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621m_merged_edge_memory.json").write_text(json.dumps(merged_list,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621m_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
