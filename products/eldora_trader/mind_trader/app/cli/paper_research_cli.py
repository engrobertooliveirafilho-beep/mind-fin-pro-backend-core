import argparse, json
from mind_trader.app.orchestration.paper_research_operation import run_paper_research_operation
from mind_trader.app.audits.preflight_check import preflight_check

def run_paper_research_cli(argv=None):
    p=argparse.ArgumentParser("mind-trader-paper-research")
    p.add_argument("--data-folder", required=True)
    p.add_argument("--symbol", required=True)
    p.add_argument("--timeframe", required=True)
    p.add_argument("--db-path", default="mind_trader/data/market.sqlite")
    p.add_argument("--ftmo-config", default="mind_trader/config/ftmo_ruleset.json")
    p.add_argument("--limit", type=int, default=10)
    args=p.parse_args(argv)

    preflight=preflight_check(args.data_folder,args.ftmo_config,tests_passed=199)

    if preflight["decision"]!="PREFLIGHT_OK":
        r={
            "decision":"CLI_BLOCKED_PREFLIGHT",
            "preflight":preflight,
            "production":"BLOCKED",
            "live":"FORBIDDEN",
            "edge_claim":"NONE"
        }
        print(json.dumps(r,ensure_ascii=False,indent=2))
        return r

    r=run_paper_research_operation(
        data_folder=args.data_folder,
        symbol=args.symbol,
        timeframe=args.timeframe,
        db_path=args.db_path,
        ftmo_config_path=args.ftmo_config,
        limit=args.limit
    )

    print(json.dumps(r,ensure_ascii=False,indent=2))
    return r

if __name__=="__main__":
    run_paper_research_cli()
