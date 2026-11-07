"""ET665 R28: audit canonical/mirror source drift without running project code."""
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

PREFIX = "products/eldora_trader/"
SENSITIVE = ("MetaTrader5", "order_send", "order_check", "subprocess", "shell=True", "rclone")
def git(root,*args):
    return subprocess.check_output(["git","-C",str(root),*args])
def inspect(source):
    text=source.decode("utf-8-sig",errors="replace")
    tokens=[x for x in SENSITIVE if x in text]
    try:
        tree=ast.parse(text)
        calls=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):
                fn=n.func
                if isinstance(fn,ast.Attribute):
                    expr=ast.unparse(fn)
                    if any(x in expr for x in ("mt5.","MetaTrader5.","subprocess.","os.system","os.popen")):
                        calls.append({"line":n.lineno,"call":expr})
        parse="PASS"
    except (SyntaxError,ValueError,RecursionError) as e:
        parse="FAIL:"+type(e).__name__
        calls=[]
    return {"tokens":tokens,"calls":calls,"parse":parse}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default=".")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    root=Path(a.repo).resolve()
    out=Path(a.output).resolve()
    if out.exists():raise SystemExit("OUTPUT_EXISTS")
    head=git(root,"rev-parse","HEAD").decode().strip()
    entries=git(root,"ls-tree","-r","-z","--full-tree","HEAD").split(b"\0")
    paths={}
    for entry in entries:
        if not entry:continue
        meta,raw=entry.split(b"\t",1)
        mode,typ,oid=meta.decode().split()
        if typ=="blob" and raw.endswith(b".py"):
            paths[raw.decode("utf-8","surrogateescape")]=oid
    pairs=[]
    for mirror,mirror_oid in sorted(paths.items()):
        if not mirror.startswith(PREFIX):continue
        canonical=mirror[len(PREFIX):]
        if not canonical.startswith("mind_trader/") or canonical not in paths:continue
        canonical_oid=paths[canonical]
        if canonical_oid==mirror_oid:continue
        mirror_source=git(root,"cat-file","blob",mirror_oid)
        canon_source=git(root,"cat-file","blob",canonical_oid)
        m=inspect(mirror_source)
        n=inspect(canon_source)
        critical=any(x in m["tokens"] for x in ("MetaTrader5","order_send","order_check","subprocess","shell=True","rclone"))
        pairs.append({"canonical":canonical,"mirror":mirror,
                      "canonical_blob":canonical_oid,"mirror_blob":mirror_oid,
                      "canonical_sha256":hashlib.sha256(canon_source).hexdigest(),
                      "mirror_sha256":hashlib.sha256(mirror_source).hexdigest(),
                      "mirror_analysis":m,"canonical_analysis":n,
                      "sensitive_drift_candidate":critical,
                      "review":"NOT_CERTIFIED"})
    report={"schema":"ET665_R28_MIRROR_DRIFT_V1","head":head,
            "python_files":len(paths),"divergent_pairs":len(pairs),
            "sensitive_drift_candidates":sum(x["sensitive_drift_candidate"] for x in pairs),
            "semantic_reachability":"NOT_CERTIFIED","phase_b":"BLOCKED","pairs":pairs}
    out.mkdir(parents=True)
    target=out/"mirror_drift.json"
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("MIRROR_DRIFT_SHA256="+hashlib.sha256(target.read_bytes()).hexdigest())
    print(json.dumps({k:v for k,v in report.items() if k!="pairs"},ensure_ascii=False))
    for row in [x for x in pairs if x["sensitive_drift_candidate"]][:60]:
        print("DRIFT | "+row["canonical"]+" | "+row["mirror"]+" | "+",".join(row["mirror_analysis"]["tokens"]))
if __name__=="__main__":main()
