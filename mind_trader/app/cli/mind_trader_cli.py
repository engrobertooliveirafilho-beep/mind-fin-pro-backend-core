import argparse, json, sys
from pathlib import Path
from mind_trader.app.orchestration.daily_research_runner import run_daily_research
from mind_trader.app.audits.institutional_audit_ledger import append_audit_event

def run_cli(argv=None):
    p=argparse.ArgumentParser("mind-trader")
    p.add_argument("--mode", choices=["daily-research"], required=True)
    p.add_argument("--symbols", default="TEST")
    p.add_argument("--timeframes", default="1m")
    p.add_argument("--db-path", default="mind_trader/data/market.sqlite")
    p.add_argument("--ftmo-config", default="mind_trader/config/ftmo_ruleset.json")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--dry-run", action="store_true")
    args=p.parse_args(argv)

    payload={
        "mode":args.mode,
        "symbols":args.symbols.split(","),
        "timeframes":args.timeframes.split(","),
        "db_path":args.db_path,
        "ftmo_config":args.ftmo_config,
        "limit":args.limit,
        "dry_run":args.dry_run,
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

    if args.dry_run:
        payload["decision"]="DRY_RUN_ONLY"
        append_audit_event("P8.51_CLI_DRY_RUN",payload)
        print(json.dumps(payload,ensure_ascii=False,indent=2))
        return payload

    result=run_daily_research(
        symbols=tuple(payload["symbols"]),
        timeframes=tuple(payload["timeframes"]),
        db_path=args.db_path,
        limit=args.limit,
        ftmo_config_path=args.ftmo_config
    )
    append_audit_event("P8.51_CLI_EXECUTED",{"decision":result["decision"],"production":"BLOCKED","live":"FORBIDDEN"})
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=="__main__":
    run_cli()
