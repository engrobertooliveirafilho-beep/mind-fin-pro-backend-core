"""ET665 R24: offline triage of R23 JSON; never imports scanned project files."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

def scope(path):
    if "/quarantine/" in path or "/runtime_quarantine/" in path or "/quarantine_v2/" in path:
        return "QUARANTINE_REVIEW_REQUIRED"
    if any(x in path.lower() for x in ("/backup", "/evidence", "/archive", "/legacy")):
        return "HISTORICAL_REVIEW_REQUIRED"
    if path.startswith("mind_trader/"):
        return "TRADER_ACTIVE_CANDIDATE"
    if path.startswith("products/eldora_trader/"):
        return "TRADER_MIRROR_CANDIDATE"
    return "OTHER_REPOSITORY"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--expected-head",required=True)
    args=p.parse_args()
    source=Path(args.inventory).resolve()
    dest=Path(args.output).resolve()
    if dest.exists(): raise SystemExit("OUTPUT_EXISTS")
    obj=json.loads(source.read_text(encoding="utf-8"))
    if obj.get("head") != args.expected_head: raise SystemExit("HEAD_MISMATCH")
    rows=obj["records"]
    if len(rows)!=obj["tracked_python_files"] or len(rows)!=obj["analyzed_python_files"]:
        raise SystemExit("COVERAGE_MISMATCH")
    kinds=collections.Counter()
    scopes=collections.Counter()
    issues=[]
    for row in rows:
        s=scope(row["path"])
        scopes[s]+=1
        if row["parse"]!="PASS":
            issues.append({"path":row["path"],"scope":s,"parse":row["parse"],"blob":row["blob"],"sha256":row["sha256"]})
        for hit in row["hits"]:
            kinds[hit["kind"]]+=1
    flagged=[]
    for row in rows:
        if not row["hits"]:continue
        group=scope(row["path"])
        relevant=[h for h in row["hits"] if h["kind"].startswith("AST_CALL:") or h["kind"] in
                  ("PROCESS_INVOCATION","ORDER_SEND_TOKEN","ORDER_CHECK_TOKEN","SHELL_TRUE_TOKEN","RCLONE_TOKEN","AST_PARSE_FAILURE")]
        if relevant:
            flagged.append({"path":row["path"],"scope":group,"blob":row["blob"],
                            "hits":relevant})
    summary={
        "schema":"ET665_R24_TRIAGE_V1",
        "source_head":obj["head"],
        "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "files":len(rows),"parse_failures":len(issues),
        "scope_counts":dict(sorted(scopes.items())),
        "kind_counts":dict(sorted(kinds.items())),
        "priority_files":len(flagged),
        "semantic_review":"NOT_CERTIFIED",
        "quarantine_is_not_automatic_exclusion":True,
        "phase_b":"BLOCKED",
    }
    dest.mkdir(parents=True)
    for name,data in (("triage_summary.json",summary),("parse_failures.json",issues),
                      ("priority_routes.json",flagged)):
        f=dest/name
        f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(name+"_SHA256="+hashlib.sha256(f.read_bytes()).hexdigest())
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
