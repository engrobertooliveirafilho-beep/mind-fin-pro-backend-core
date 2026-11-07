"""ET665 R26: deterministic offline priority queue, never executes scanned files."""
import argparse
import hashlib
import json
from pathlib import Path

WEIGHTS={"ORDER_SEND_TOKEN":100,"ORDER_CHECK_TOKEN":70,"AST_CALL:mt5":60,
         "PROCESS_INVOCATION":45,"SHELL_TRUE_TOKEN":40,"RCLONE_TOKEN":35,
         "AST_CALL:process":30,"AST_CALL:network":20,"AST_CALL:dynamic":10,
         "AST_PARSE_FAILURE":100}
def score(hit):
    kind=hit["kind"]
    return WEIGHTS.get(kind, 5 if kind.startswith("AST_CALL:") else 0)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--triage",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    inp=Path(a.triage).resolve()
    out=Path(a.output).resolve()
    if out.exists():raise SystemExit("OUTPUT_EXISTS")
    rows=json.loads((inp/"priority_routes.json").read_text(encoding="utf-8"))
    failures=json.loads((inp/"parse_failures.json").read_text(encoding="utf-8"))
    queue=[]
    for row in rows:
        if row["scope"] not in ("TRADER_ACTIVE_CANDIDATE","TRADER_MIRROR_CANDIDATE"):
            continue
        hits=row["hits"]
        bykind={}
        for h in hits:bykind[h["kind"]]=bykind.get(h["kind"],0)+1
        queue.append({"path":row["path"],"scope":row["scope"],"blob":row["blob"],
                      "score":sum(score(h) for h in hits),
                      "kinds":bykind,"review_status":"UNREVIEWED"})
    queue.sort(key=lambda x:(-x["score"],x["path"]))
    trader_failures=[x for x in failures if x["scope"] in ("TRADER_ACTIVE_CANDIDATE","TRADER_MIRROR_CANDIDATE")]
    manifest={"schema":"ET665_R26_TRADER_PRIORITY_V1",
              "input_priority_sha256":hashlib.sha256((inp/"priority_routes.json").read_bytes()).hexdigest(),
              "input_failures_sha256":hashlib.sha256((inp/"parse_failures.json").read_bytes()).hexdigest(),
              "trader_priority_files":len(queue),"trader_parse_failures":trader_failures,
              "non_trader_scope_not_excluded":True,
              "reviewed":0,"semantic_review":"NOT_CERTIFIED","phase_b":"BLOCKED",
              "queue":queue}
    out.mkdir(parents=True)
    p=out/"trader_priority_queue.json"
    p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TRADER_QUEUE_SHA256="+hashlib.sha256(p.read_bytes()).hexdigest())
    print(json.dumps({k:v for k,v in manifest.items() if k!="queue"},ensure_ascii=False))
    print("TOP_30_PRIORITY_ROUTES")
    for item in queue[:30]:
        print(str(item["score"])+" | "+item["scope"]+" | "+item["path"]+" | "+",".join(item["kinds"]))
if __name__=="__main__":main()
