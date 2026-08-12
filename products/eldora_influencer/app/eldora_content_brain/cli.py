from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import BrainSettings
from .pipeline import ContentBrainPipeline


def main() -> int:
    parser = argparse.ArgumentParser(prog="eldora-content-brain")
    parser.add_argument("mode", choices=["research", "latest"])
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    pipeline = ContentBrainPipeline(BrainSettings.load(args.config))

    if args.mode == "research":
        print(pipeline.run_research())
        return 0

    root, plan = pipeline.load_latest_plan()
    print(json.dumps({
        "run_root": str(root),
        "decisions": len(plan.get("decisions", [])),
        "evidence": len(plan.get("evidence", [])),
        "rejected_trends": len(plan.get("rejected_trends", [])),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())