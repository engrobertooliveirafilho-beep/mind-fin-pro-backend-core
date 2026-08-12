import json
import argparse
from pathlib import Path

from app.runtime.drive_batch_processor import process_folder

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    result = process_folder(args.folder, recursive=not args.no_recursive)
    text = json.dumps(result, indent=2, ensure_ascii=False, default=str)

    print(text)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()
