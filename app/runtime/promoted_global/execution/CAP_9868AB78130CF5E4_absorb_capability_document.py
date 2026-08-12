import json
import argparse
from pathlib import Path

from app.runtime.drive_capability_absorption import absorb_text_source

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    p = Path(args.file)
    text = p.read_text(encoding="utf-8", errors="ignore")

    result = absorb_text_source(
        source_id=args.source,
        text=text,
        metadata={"file": str(p)}
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
