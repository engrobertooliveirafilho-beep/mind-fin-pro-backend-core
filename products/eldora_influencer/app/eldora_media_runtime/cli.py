from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import Settings
from .pipeline import EldoraMediaPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eldora-media")
    parser.add_argument("mode", choices=["audit", "plan", "produce"])
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--config", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = Settings.load(args.config)
    pipeline = EldoraMediaPipeline(settings)

    if args.mode == "audit":
        print(json.dumps(pipeline.audit(), ensure_ascii=False, indent=2))
        return 0

    if args.mode == "plan":
        print(pipeline.plan(count=args.count))
        return 0

    print(pipeline.produce(count=args.count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())