import json
import argparse
from pathlib import Path

from app.runtime.knowledge_extraction_engine import extract_items

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    p = Path(args.file)
    text = p.read_text(encoding="utf-8", errors="ignore")

    result = extract_items(
        source_id=args.source,
        text=text,
        metadata={"file": str(p)}
    )

    payload = json.dumps(result, indent=2, ensure_ascii=False)
    print(payload)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(payload, encoding="utf-8")

if __name__ == "__main__":
    main()
