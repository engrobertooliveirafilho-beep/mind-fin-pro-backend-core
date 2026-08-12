from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import StudioConfig
from .orchestrator import EldoraAIStudio


def main() -> int:
    parser = argparse.ArgumentParser(prog="eldora-ai-studio")
    parser.add_argument("mode", choices=["audit", "research", "generate", "latest"])
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    studio = EldoraAIStudio(StudioConfig.load(args.config))

    if args.mode == "audit":
        print(json.dumps(studio.audit(), ensure_ascii=False, indent=2))
        return 0
    if args.mode == "research":
        print(studio.research())
        return 0
    if args.mode == "generate":
        print(studio.generate_candidate())
        return 0

    print(json.dumps(studio.latest(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())