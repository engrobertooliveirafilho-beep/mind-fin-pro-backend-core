import json, subprocess
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P16.22_AUTONOMOUS_DAILY_RESEARCH_CRON")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

PIPELINE=[
 "app.p1621b_youtube_absorption_engine.engine",
 "app.p1621e_real_video_fetch_loop.engine",
 "app.p1621f_transcript_download_strategy_extraction.engine",
 "app.p1621g_rule_normalization_auto_backtest.engine",
 "app.p1621k_video_strategy_backtest_executor.engine",
 "app.p1621l_video_strategy_wf_mc.engine",
 "app.p1621m_video_edge_memory_merge.engine",
 "app.p1621o_edge_factory_master_certification.engine"
]

def run_module(module):
    p=subprocess.run(["python","-m",module],capture_output=True,text=True,timeout=900)
    return {"module":module,"returncode":p.returncode,"stdout":p.stdout[-2000:],"stderr":p.stderr[-2000:]}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    results=[run_module(m) for m in PIPELINE]
    ok=all(x["returncode"]==0 for x in results)
    report={
        "STATUS":"P16.22_AUTONOMOUS_DAILY_RESEARCH_CRON_IMPLEMENTED" if ok else "P16.22_CRON_RUN_FAILED",
        "PIPELINE_STEPS":len(PIPELINE),
        "SUCCESS":ok,
        "FAILED_MODULES":[x["module"] for x in results if x["returncode"]!=0],
        "MODE":"MANUAL_OR_OS_CRON",
        "SCHEDULE_HINT":"Run daily with Windows Task Scheduler or cron.",
        "NEXT":"P16.23_EDGE_DECAY_REVALIDATION_AND_AUTO_ARCHIVE",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1622_run_log.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1622_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
