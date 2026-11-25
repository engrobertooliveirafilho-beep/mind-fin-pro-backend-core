import json, math
from pathlib import Path
from datetime import datetime,UTC
from collections import Counter

INPUT=Path("reports/P15.6_P15.10_REAL_EDGE_RESEARCH_RUNTIME/promoted_edges.json")

def valid_record(e):
    if not isinstance(e,dict):
        return False
    try:
        return (all(isinstance(e.get(k),str) and e[k].strip() for k in ("symbol","timeframe"))
                and type(e.get("profit_factor")) in (int,float)
                and math.isfinite(e["profit_factor"]) and e["profit_factor"]>=0
                and type(e.get("trades")) is int and e["trades"]>=0
                and all(type(e.get(k)) is bool for k in ("walk_forward_approved","monte_carlo_approved")))
    except (OverflowError,ValueError,TypeError):
        return False

def run():

    promoted=json.loads(INPUT.read_text(encoding="utf-8"))

    if not isinstance(promoted,list):
        raise ValueError("INVALID_FORENSIC_INPUT")

    symbols=Counter()
    timeframes=Counter()

    approved=[]
    rejected=[]

    invalid_count=0
    for e in promoted:
        if not valid_record(e):
            invalid_count+=1
            continue
        e=dict(e)

        symbols[e["symbol"]]+=1
        timeframes[e["timeframe"]]+=1

        score=0

        if e["profit_factor"]>=1.50:
            score+=3

        elif e["profit_factor"]>=1.30:
            score+=2

        elif e["profit_factor"]>=1.25:
            score+=1

        if e["trades"]>=30:
            score+=3

        elif e["trades"]>=20:
            score+=2

        elif e["trades"]>=10:
            score+=1

        if e["walk_forward_approved"]:
            score+=2

        if e["monte_carlo_approved"]:
            score+=2

        e["forensic_score"]=score

        if score>=7:
            approved.append(e)
        else:
            rejected.append(e)

    approved.sort(
        key=lambda x:x["forensic_score"],
        reverse=True
    )

    report={

        "STATUS":"P15.11_PROMOTED_EDGE_FORENSIC_AUDIT",

        "PROMOTED_INPUT":len(promoted),

        "FORENSIC_APPROVED":len(approved),

        "FORENSIC_REJECTED":len(rejected)+invalid_count,
        "INVALID_INPUT_COUNT":invalid_count,

        "TOP_SYMBOLS":symbols.most_common(10),

        "TOP_TIMEFRAMES":timeframes.most_common(10),

        "TOP_10_EDGES":approved[:10],

        "NEXT":"P15.12_EDGE_PROMOTION_AUTHORITY",

        "generated_at":datetime.now(UTC).isoformat()
    }

    out=Path(
        "reports/P15.11_PROMOTED_EDGE_FORENSIC_AUDIT"
    )

    out.mkdir(parents=True,exist_ok=True)

    (out/"approved_edges.json").write_text(
        json.dumps(
            approved,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    (out/"rejected_edges.json").write_text(
        json.dumps(
            rejected,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    (out/"forensic_audit.json").write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return report

if __name__=="__main__":
    print(
        json.dumps(
            run(),
            indent=2,
            ensure_ascii=False
        )
    )
