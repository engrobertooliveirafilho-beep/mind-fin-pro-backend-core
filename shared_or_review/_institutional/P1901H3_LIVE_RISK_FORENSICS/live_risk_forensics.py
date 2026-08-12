from pathlib import Path
import json
import ast


TERMS = [
    "order_send(",
    "send_order(",
    "trade_live",
    "live_trading",
    "real_order",
    "real_orders",
    "ftmo_real",
    "mt5_real",
    "order_sent",
    "mt5.order_send",
]

SAFE_CONTEXT = [
    "forbidden",
    "blocked",
    "research_only",
    "paper_only",
    "false",
    "none",
    "never",
    "disabled",
    "safety",
    "lock",
    "guard",
    "assert",
    "test",
    "mock",
    "stub",
    "simulation",
]

DANGER_CONTEXT = [
    "true",
    "enabled",
    "live",
    "execute",
    "place",
    "broker",
    "account",
    "password",
    "login",
]


def is_test_file(path: Path) -> bool:
    s = str(path).replace("\\", "/").lower()
    return "/tests/" in s or s.startswith("tests/") or "test_" in path.name.lower()


def is_comment(line: str) -> bool:
    return line.strip().startswith("#")


def window(lines, index, radius=3):
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(lines[start:end])


def classify(path: Path, line: str, context: str) -> str:
    low = (line + "\n" + context).lower()

    if is_comment(line):
        return "SAFE_COMMENT"

    if is_test_file(path):
        if "assert" in low or any(s in low for s in SAFE_CONTEXT):
            return "SAFE_TEST"

    if "assert" in low and any(s in low for s in SAFE_CONTEXT):
        return "SAFE_ASSERT"

    if any(s in low for s in ["forbidden", "blocked", "research_only", "paper_only", "never", "disabled"]):
        return "SAFE_FORBIDDEN"

    if any(s in low for s in ["mock", "stub", "simulation"]):
        return "SAFE_STUB"

    if "order_send(" in low or "send_order(" in low or "mt5.order_send" in low:
        if any(s in low for s in SAFE_CONTEXT):
            return "SAFE_BLOCKED_EXECUTION_REFERENCE"
        return "LIVE_EXECUTION_RISK"

    danger_score = sum(low.count(x) for x in DANGER_CONTEXT)
    safe_score = sum(low.count(x) for x in SAFE_CONTEXT)

    if danger_score > safe_score and danger_score >= 2:
        return "REQUIRES_MANUAL_REVIEW"

    return "SAFE_REFERENCE"


def scan_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    hits = []

    for idx, line in enumerate(lines):
        low = line.lower()
        for term in TERMS:
            if term in low:
                ctx = window(lines, idx)
                hits.append({
                    "file": str(path).replace("\\", "/"),
                    "line": idx + 1,
                    "term": term,
                    "classification": classify(path, line, ctx),
                    "content": line.strip()[:300],
                    "context": ctx.strip()[:800],
                })

    return hits


def run():
    all_hits = []

    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files", "--", "*.py"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout.splitlines()

    for item in tracked:
        path = Path(item)
        if path.is_file():
            all_hits.extend(scan_file(path))

    blocking = [
        h for h in all_hits
        if h["classification"] in ["LIVE_EXECUTION_RISK", "REQUIRES_MANUAL_REVIEW"]
    ]

    summary_by_class = {}
    for h in all_hits:
        summary_by_class[h["classification"]] = summary_by_class.get(h["classification"], 0) + 1

    result = {
        "program": "P1901H3_LIVE_RISK_FORENSICS",
        "status": "PASS" if not blocking else "BLOCKED",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "total_hits": len(all_hits),
        "blocking_hits": len(blocking),
        "summary_by_class": summary_by_class,
        "approved_for_P1901I": len(blocking) == 0,
        "blocking": blocking,
        "hits": all_hits,
    }

    out = Path("_evidence/P1901H3/LIVE_RISK_FORENSICS.json")
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "program": result["program"],
        "status": result["status"],
        "mode": result["mode"],
        "total_hits": result["total_hits"],
        "blocking_hits": result["blocking_hits"],
        "summary_by_class": result["summary_by_class"],
        "approved_for_P1901I": result["approved_for_P1901I"],
        "report": str(out),
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
