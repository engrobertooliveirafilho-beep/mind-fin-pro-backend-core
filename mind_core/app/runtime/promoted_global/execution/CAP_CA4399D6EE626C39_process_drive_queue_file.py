import json
import argparse

from app.runtime.drive_processed_queue import process_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--no-move", action="store_true")
    args = parser.parse_args()

    out = process_file(args.file, move=not args.no_move)
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
