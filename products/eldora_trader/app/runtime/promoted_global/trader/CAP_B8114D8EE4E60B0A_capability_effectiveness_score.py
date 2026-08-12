import json
from pathlib import Path

LEDGER = Path("runtime/capability_usage_ledger.jsonl")

def build_scorecard():

    scores = {}

    if not LEDGER.exists():
        return {}

    for line in LEDGER.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines():

        try:
            row = json.loads(line)
        except:
            continue

        cap = row.get("capability")

        if not cap:
            continue

        scores.setdefault(cap,{
            "usage":0,
            "success":0,
            "failed":0,
            "latency_total":0
        })

        scores[cap]["usage"] += 1

        if row.get("success"):
            scores[cap]["success"] += 1
        else:
            scores[cap]["failed"] += 1

        scores[cap]["latency_total"] += float(
            row.get("latency_ms",0)
        )

    final = {}

    for cap,data in scores.items():

        usage = data["usage"]

        success_rate = (
            data["success"] / usage
        ) if usage else 0

        avg_latency = (
            data["latency_total"] / usage
        ) if usage else 0

        effectiveness = round(
            (
                success_rate * 80
            ) +
            (
                min(usage,100)/100 * 20
            )
        )

        final[cap] = {
            "usage": usage,
            "success_rate": round(success_rate,4),
            "avg_latency_ms": round(avg_latency,2),
            "effectiveness_score": effectiveness
        }

    return dict(
        sorted(
            final.items(),
            key=lambda x:x[1]["effectiveness_score"],
            reverse=True
        )
    )

if __name__ == "__main__":

    result = build_scorecard()

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )
