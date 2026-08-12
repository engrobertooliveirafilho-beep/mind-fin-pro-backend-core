import json
import argparse
import os
from pathlib import Path
from datetime import datetime, timezone


def load_env():
    p = Path(".env")
    if p.exists():
        for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="whatsapp:+5519996166906")
    parser.add_argument("--message", default="Use retrieval e memória social: qual é meu nome e o que estou estudando?")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    load_env()

    from app.runtime.capability_orchestrator import capability_orchestrator

    result = capability_orchestrator(args.user, args.message, mode="diagnostic")

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "diagnostic": result,
        "summary": {
            "status": result.get("status"),
            "available": len(result.get("capabilities_available", [])),
            "used": len(result.get("capabilities_used", [])),
            "failed": len(result.get("capabilities_failed", [])),
            "recommended": result.get("capabilities_recommended", []),
        }
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    print(text)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")

    if result.get("status") not in ["ok", "partial"]:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
