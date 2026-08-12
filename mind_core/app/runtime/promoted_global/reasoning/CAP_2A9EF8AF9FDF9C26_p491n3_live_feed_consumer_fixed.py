import os, csv, json, time, ast, hashlib, traceback
from pathlib import Path
from datetime import datetime

BACKEND = Path(os.environ["P491N3_BACKEND"])
EVIDENCE = Path(os.environ["P491N3_EVIDENCE"])

FEEDS = [
    Path(os.environ["P491N3_MIND_ITEMS"]),
    Path(os.environ["P491N3_RUNTIME"]),
    Path(os.environ["P491N3_CODE_MATRIX"]),
    Path(os.environ["P491N3_CAPABILITY"]),
]

MANIFEST = EVIDENCE / "capability_manifest.jsonl"
DEPENDENCY = EVIDENCE / "dependency_map.jsonl"
RUNTIME = EVIDENCE / "runtime_recovery_results.jsonl"
INTEGRATION = EVIDENCE / "integration_readiness.jsonl"
LEDGER = EVIDENCE / "processed_ledger_p491n3.jsonl"
STATUS = EVIDENCE / "loop_status.json"
SUMMARY = EVIDENCE / "summary.json"
UNRESOLVED = EVIDENCE / "unresolved_paths.jsonl"

ALLOW = [
    "mind","eldora","neura","memory","retrieval","vector","runtime",
    "agent","supabase","fastapi","whatsapp","orchestration","social",
    "longterm","long_term"
]

BLOCK_CANDIDATE = [
    "node_modules","vendor","site-packages","__pycache__","coverage",
    "htmlcov","audit","ledger","snapshot","mind_evidence",
    "_control","control","reports"
]

processed = set()
fingerprints = {}

def now():
    return datetime.now().isoformat()

def write_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def allowed(s):
    s = str(s).lower()
    return any(x in s for x in ALLOW)

def blocked_candidate(s):
    s = str(s).lower()
    return any(x in s for x in BLOCK_CANDIDATE)

def read_text_safe(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def get_candidate_path(row):
    keys = [
        "path","file","filepath","fullpath","full_path",
        "source_path","drive_path","local_path","name",
        "remote","remote_path","item_path"
    ]
    for k in keys:
        if k in row and str(row[k]).strip():
            return str(row[k]).strip()
    for v in row.values():
        if v and (".py" in str(v).lower() or "/" in str(v) or "\\" in str(v)):
            return str(v).strip()
    return None

def heuristic_score(path, text, row):
    blob = (str(path) + "\n" + json.dumps(row, ensure_ascii=False) + "\n" + text[:5000]).lower()
    pts = sum(1 for k in ALLOW if k in blob)
    if "class " in text or "def " in text:
        pts += 2
    if "import " in text:
        pts += 1
    if "fastapi" in blob or "supabase" in blob or "twilio" in blob:
        pts += 2
    if "memory" in blob or "retrieval" in blob or "agent" in blob:
        pts += 2
    return 5 if pts >= 6 else 4 if pts >= 4 else 3 if pts >= 2 else 0

def get_score(row, text, path):
    for k in ["score","priority_score","final_score","value_score","relevance","relevance_score"]:
        if k in row and str(row[k]).strip():
            try:
                v = float(str(row[k]).replace(",", "."))
                if v >= 5: return 5
                if v >= 4: return 4
                if v >= 3: return 3
            except Exception:
                pass
    return heuristic_score(path, text, row)

def read_csv(path):
    rows = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
            sample = f.read(8192)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;")
            except Exception:
                dialect = csv.excel
            reader = csv.DictReader(f, dialect=dialect)
            for row in reader:
                rows.append(row)
    except Exception as e:
        write_jsonl(UNRESOLVED, {"feed":str(path),"error":"csv_read_failed","detail":str(e),"timestamp":now()})
    return rows

def read_jsonl(path):
    rows = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception as e:
        write_jsonl(UNRESOLVED, {"feed":str(path),"error":"jsonl_read_failed","detail":str(e),"timestamp":now()})
    return rows

def load_feed(path):
    if not path.exists():
        write_jsonl(UNRESOLVED, {"feed":str(path),"error":"feed_not_found","timestamp":now()})
        return []
    if path.suffix.lower() == ".jsonl":
        return read_jsonl(path)
    return read_csv(path)

def resolve_path(raw):
    s = str(raw).strip().strip('"')
    p = Path(s)
    if p.exists():
        return p

    if s.lower().startswith("gdrive:") or s.lower().startswith("google drive"):
        return None

    name = Path(s).name
    if not name:
        return None

    hits = []
    try:
        hits = list(BACKEND.rglob(name))
    except Exception:
        hits = []

    hits = [h for h in hits if h.exists() and not blocked_candidate(h)]
    if hits:
        return hits[0]

    return None

def ast_manifest(path, text):
    out = {"path":str(path), "classes":[], "functions":[], "imports":[], "syntax_ok":False}
    try:
        tree = ast.parse(text)
        out["syntax_ok"] = True
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                out["classes"].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                out["functions"].append(node.name)
            elif isinstance(node, ast.Import):
                for n in node.names:
                    out["imports"].append(n.name)
            elif isinstance(node, ast.ImportFrom):
                out["imports"].append(node.module or "")
    except Exception as e:
        out["syntax_error"] = str(e)
    return out

def fingerprint(text):
    norm = "\n".join(
        l.strip()
        for l in text.splitlines()
        if l.strip() and not l.strip().startswith("#")
    )
    return hashlib.sha256(norm.encode("utf-8", errors="ignore")).hexdigest()

def classify(manifest):
    if not manifest.get("syntax_ok"):
        return "BROKEN"
    if manifest.get("classes") or manifest.get("functions"):
        return "RUNS_WITH_FIX"
    return "NEEDS_MANUAL_REVIEW"

def integration(path, text, manifest):
    blob = (str(path) + "\n" + text[:5000]).lower()
    targets = [k.upper() for k in ALLOW if k in blob]
    readiness = "YES" if manifest.get("syntax_ok") and len(targets) >= 2 else "PARTIAL" if targets else "NO"
    return {"path":str(path), "readiness":readiness, "targets":targets, "timestamp":now()}

def collect():
    rows_out = []
    feed_status = []

    for feed in FEEDS:
        rows = load_feed(feed)
        feed_status.append({
            "feed": str(feed),
            "exists": feed.exists(),
            "rows": len(rows),
            "last_write": datetime.fromtimestamp(feed.stat().st_mtime).isoformat() if feed.exists() else None
        })

        for row in rows:
            raw = get_candidate_path(row)
            if not raw:
                continue
            if not allowed(raw):
                continue
            if blocked_candidate(raw):
                continue
            rows_out.append((raw, row, str(feed)))

    return rows_out, feed_status

def main():
    SUMMARY.write_text(json.dumps({
        "mission":"P4.91N3",
        "status":"STARTED",
        "mode":"EXPLICIT_FEED_PATHS",
        "priority":"SCORE_5_THEN_4_THEN_3",
        "delete":"FORBIDDEN",
        "move_original":"FORBIDDEN",
        "modify_original":"FORBIDDEN",
        "feeds":[str(x) for x in FEEDS],
        "started_at":now(),
        "evidence":str(EVIDENCE)
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    cycle = 0

    while True:
        cycle += 1
        rows, feed_status = collect()

        buckets = {5:[],4:[],3:[]}
        unresolved = 0

        for raw, row, feed in rows:
            key = f"{feed}|{raw}"
            if key in processed:
                continue

            rp = resolve_path(raw)
            if not rp:
                unresolved += 1
                if unresolved <= 100:
                    write_jsonl(UNRESOLVED, {
                        "raw_path":raw,
                        "feed":feed,
                        "reason":"cannot_resolve_local_path",
                        "timestamp":now()
                    })
                continue

            text = read_text_safe(rp)
            score = get_score(row, text, rp)
            if score in buckets:
                buckets[score].append((rp,row,feed,text,key,raw))

        selected_score = None
        batch = []
        for s in [5,4,3]:
            if buckets[s]:
                selected_score = s
                batch = buckets[s][:100]
                break

        status = {
            "mission":"P4.91N3",
            "cycle":cycle,
            "timestamp":now(),
            "feed_status":feed_status,
            "pending_score_5":len(buckets[5]),
            "pending_score_4":len(buckets[4]),
            "pending_score_3":len(buckets[3]),
            "selected_score":selected_score,
            "selected_batch":len(batch),
            "processed_total":len(processed),
            "unresolved_paths":unresolved,
            "mode":"EXPLICIT_FEED_LOOP"
        }

        STATUS.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")

        print("="*100)
        print("P4.91N3 LIVE FEED CONSUMER FIXED")
        print(json.dumps(status, indent=2, ensure_ascii=False))

        if not batch:
            time.sleep(30)
            continue

        for rp,row,feed,text,key,raw in batch:
            try:
                fp = fingerprint(text)
                dup = fp in fingerprints
                manifest = ast_manifest(rp,text)
                manifest.update({
                    "mission":"P4.91N3",
                    "score":selected_score,
                    "feed":feed,
                    "raw_path":raw,
                    "fingerprint":fp,
                    "duplicate":dup,
                    "duplicate_of":fingerprints.get(fp),
                    "timestamp":now()
                })

                final = "DUPLICATE_LOWER_VALUE" if dup else classify(manifest)
                if not dup:
                    fingerprints[fp] = str(rp)

                deps = {
                    "path":str(rp),
                    "raw_path":raw,
                    "score":selected_score,
                    "feed":feed,
                    "imports":manifest.get("imports",[]),
                    "classes":manifest.get("classes",[]),
                    "functions":manifest.get("functions",[]),
                    "timestamp":now()
                }

                integ = integration(rp,text,manifest)

                runtime = {
                    "path":str(rp),
                    "raw_path":raw,
                    "score":selected_score,
                    "status_final":final,
                    "syntax_ok":manifest.get("syntax_ok"),
                    "feed":feed,
                    "timestamp":now()
                }

                ledger = {
                    "path":str(rp),
                    "raw_path":raw,
                    "score":selected_score,
                    "status_final":final,
                    "fingerprint":fp,
                    "feed":feed,
                    "timestamp":now()
                }

                write_jsonl(MANIFEST,manifest)
                write_jsonl(DEPENDENCY,deps)
                write_jsonl(INTEGRATION,integ)
                write_jsonl(RUNTIME,runtime)
                write_jsonl(LEDGER,ledger)
                processed.add(key)

            except Exception as e:
                write_jsonl(RUNTIME,{
                    "path":str(rp),
                    "raw_path":raw,
                    "score":selected_score,
                    "status_final":"BROKEN",
                    "error":str(e),
                    "trace":traceback.format_exc(),
                    "timestamp":now()
                })
                processed.add(key)

        time.sleep(5)

if __name__ == "__main__":
    main()
