import json
import argparse
from pathlib import Path

from app.runtime.capability_reconstruction_planner import plan_from_extraction

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extraction", required=True)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    extraction = json.loads(Path(args.extraction).read_text(encoding="utf-8"))
    plan = plan_from_extraction(extraction)

    text = json.dumps(plan, indent=2, ensure_ascii=False)
    print(text)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()
