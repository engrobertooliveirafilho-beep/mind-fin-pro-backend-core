import os, csv, json, time, ast, hashlib, traceback
from pathlib import Path
from datetime import datetime

BACKEND = Path(os.environ["P491N5_BACKEND"])
EVIDENCE = Path(os.environ["P491N5_EVIDENCE"])

FEEDS = [
    ("runtime", Path(os.environ["P491N5_RUNTIME"])),
    ("code_matrix", Path(os.environ["P491N5_CODE_MATRIX"])),
    ("capability", Path(os.environ["P491N5_CAPABILITY"])),
    ("mind_items", Path(os.environ["P491N5_MIND_ITEMS"])),
]

MANIFEST = EVIDENCE / "capability_manifest.jsonl"
DEPENDENCY = EVIDENCE / "dependency_map.jsonl"
RUNTIME = EVIDENCE / "runtime_recovery_results.jsonl"
INTEGRATION = EVIDENCE / "integration_readiness.jsonl"
LEDGER = EVIDENCE / "processed_ledger_p491n5.jsonl"
STATUS = EVIDENCE / "loop_status.json"
SUMMARY = EVIDENCE / "summary.json"
CURSOR = EVIDENCE / "cursor_state.json"
UNRESOLVED = EVIDENCE / "unresolved_paths.jsonl"

ALLOW = ["mind","eldora","neura","memory","retrieval","vector","runtime","agent","supabase","fastapi","whatsapp","orchestration","social","longterm","long_term"]
BLOCK = ["node_modules","vendor","site-packages","__pycache__","coverage","htmlcov","audit","ledger","snapshot","mind_evidence","_control","control","reports"]

BATCH_SCAN_LINES = 10000
BATCH_PROCESS = 100

processed = set()
fingerprints = {}
name_index = {}

def now():
    return datetime.now().isoformat()

def write_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def blocked(s):
    s = str(s).lower()
    return any(x in s for x in BLOCK)

def allowed(s):
    s = str(s).lower()
    return any(x in s for x in ALLOW)

def build_index():
    global name_index
    count = 0
    for p in BACKEND.rglob("*.py"):
        if blocked(p):
            continue
        name_index.setdefault(p.name.lower(), []).append(p)
        count += 1
    return count

def load_cursor():
    if CURSOR.exists():
        try: return json.loads(CURSOR.read_text(encoding="utf-8"))
        except: return {}
    return {}

def save_cursor(state):
    CURSOR.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def read_text_safe(path):
    try: return Path(path).read_text(encoding="utf-8", errors="replace")
    except: return ""

def get_candidate_path(row):
    for k in ["path","file","filepath","fullpath","full_path","source_path","drive_path","local_path","name","remote","remote_path","item_path"]:
        if k in row and str(row[k]).strip():
            return str(row[k]).strip()
    for v in row.values():
        sv = str(v)
        if ".py" in sv.lower() or "/" in sv or "\\" in sv:
            return sv.strip()
    return None

def resolve_path(raw):
    s = str(raw).strip().strip('"')
    p = Path(s)
    if p.exists():
        return p
    name = Path(s).name.lower()
    hits = name_index.get(name, [])
    return hits[0] if hits else None

def heuristic_score(path, text, row):
    blob = (str(path) + "\n" + json.dumps(row, ensure_ascii=False) + "\n" + text[:3000]).lower()
    pts = sum(1 for k in ALLOW if k in blob)
    if "class " in text or "def " in text: pts += 2
    if "import " in text: pts += 1
    if "fastapi" in blob or "supabase" in blob or "twilio" in blob: pts += 2
    if "memory" in blob or "retrieval" in blob or "agent" in blob: pts += 2
    return 5 if pts >= 6 else 4 if pts >= 4 else 3 if pts >= 2 else 0

def get_score(row, text, path):
    for k in ["score","priority_score","final_score","value_score","relevance","relevance_score"]:
        if k in row and str(row[k]).strip():
            try:
                v = float(str(row[k]).replace(",", "."))
                if v >= 5: return 5
                if v >= 4: return 4
                if v >= 3: return 3
            except: pass
    return heuristic_score(path, text, row)

def stream_jsonl(feed_name, path, start_line):
    rows, last_line, scanned = [], start_line, 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if i < start_line: continue
            scanned += 1
            last_line = i + 1
            if scanned > BATCH_SCAN_LINES: break
            try: row = json.loads(line)
            except: continue
            raw = get_candidate_path(row)
            if raw and allowed(raw) and not blocked(raw):
                rows.append((raw,row,str(path),feed_name))
    return rows, last_line, scanned

def stream_csv(feed_name, path, start_line):
    rows, last_line, scanned = [], start_line, 0
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        sample = f.read(8192); f.seek(0)
        try: dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        except: dialect = csv.excel
        reader = csv.DictReader(f, dialect=dialect)
        for i, row in enumerate(reader):
            if i < start_line: continue
            scanned += 1
            last_line = i + 1
            if scanned > BATCH_SCAN_LINES: break
            raw = get_candidate_path(row)
            if raw and allowed(raw) and not blocked(raw):
                rows.append((raw,row,str(path),feed_name))
    return rows, last_line, scanned

def ast_manifest(path, text):
    out = {"path":str(path),"classes":[],"functions":[],"imports":[],"syntax_ok":False}
    try:
        tree = ast.parse(text); out["syntax_ok"] = True
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef): out["classes"].append(node.name)
            elif isinstance(node, ast.FunctionDef): out["functions"].append(node.name)
            elif isinstance(node, ast.Import):
                for n in node.names: out["imports"].append(n.name)
            elif isinstance(node, ast.ImportFrom): out["imports"].append(node.module or "")
    except Exception as e:
        out["syntax_error"] = str(e)
    return out

def fingerprint(text):
    norm = "\n".join(l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#"))
    return hashlib.sha256(norm.encode("utf-8", errors="ignore")).hexdigest()

def classify(m):
    if not m.get("syntax_ok"): return "BROKEN"
    if m.get("classes") or m.get("functions"): return "RUNS_WITH_FIX"
    return "NEEDS_MANUAL_REVIEW"

def integration(path,text,manifest):
    blob = (str(path) + "\n" + text[:3000]).lower()
    targets = [k.upper() for k in ALLOW if k in blob]
    readiness = "YES" if manifest.get("syntax_ok") and len(targets) >= 2 else "PARTIAL" if targets else "NO"
    return {"path":str(path),"readiness":readiness,"targets":targets,"timestamp":now()}

def collect(cursor):
    rows, feed_status = [], []
    for feed_name, path in FEEDS:
        key = str(path)
        start = int(cursor.get(key, 0))
        if not path.exists():
            feed_status.append({"feed":key,"exists":False})
            continue
        try:
            if path.suffix.lower() == ".jsonl":
                got,last,scanned = stream_jsonl(feed_name,path,start)
            else:
                got,last,scanned = stream_csv(feed_name,path,start)
            cursor[key] = last
            rows.extend(got)
            feed_status.append({"feed":key,"exists":True,"start_line":start,"last_line":last,"scanned":scanned,"accepted":len(got),"size":path.stat().st_size})
        except Exception as e:
            feed_status.append({"feed":key,"exists":True,"error":str(e)})
    return rows, feed_status, cursor

def process_batch(batch, selected_score):
    for rp,row,feed,text,key,raw,feed_name in batch:
        try:
            fp = fingerprint(text)
            dup = fp in fingerprints
            manifest = ast_manifest(rp,text)
            manifest.update({"mission":"P4.91N5","score":selected_score,"feed":feed,"feed_name":feed_name,"raw_path":raw,"fingerprint":fp,"duplicate":dup,"duplicate_of":fingerprints.get(fp),"timestamp":now()})
            final = "DUPLICATE_LOWER_VALUE" if dup else classify(manifest)
            if not dup: fingerprints[fp] = str(rp)
            deps = {"path":str(rp),"raw_path":raw,"score":selected_score,"feed":feed,"feed_name":feed_name,"imports":manifest.get("imports",[]),"classes":manifest.get("classes",[]),"functions":manifest.get("functions",[]),"timestamp":now()}
            integ = integration(rp,text,manifest)
            runtime = {"path":str(rp),"raw_path":raw,"score":selected_score,"status_final":final,"syntax_ok":manifest.get("syntax_ok"),"feed":feed,"feed_name":feed_name,"timestamp":now()}
            ledger = {"path":str(rp),"raw_path":raw,"score":selected_score,"status_final":final,"fingerprint":fp,"feed":feed,"feed_name":feed_name,"timestamp":now()}
            write_jsonl(MANIFEST,manifest); write_jsonl(DEPENDENCY,deps); write_jsonl(INTEGRATION,integ); write_jsonl(RUNTIME,runtime); write_jsonl(LEDGER,ledger)
            processed.add(key)
        except Exception as e:
            write_jsonl(RUNTIME,{"path":str(rp),"raw_path":raw,"score":selected_score,"status_final":"BROKEN","error":str(e),"trace":traceback.format_exc(),"timestamp":now()})
            processed.add(key)

def main():
    index_count = build_index()
    SUMMARY.write_text(json.dumps({"mission":"P4.91N5","status":"STARTED","mode":"FAST_INDEX_STREAMING","index_count":index_count,"started_at":now(),"evidence":str(EVIDENCE)}, indent=2, ensure_ascii=False), encoding="utf-8")
    print("INDEX_READY", index_count, flush=True)

    cursor = load_cursor()
    cycle = 0

    while True:
        cycle += 1
        rows, feed_status, cursor = collect(cursor)
        save_cursor(cursor)

        buckets = {5:[],4:[],3:[]}
        unresolved = 0

        for raw,row,feed,feed_name in rows:
            key = f"{feed}|{raw}"
            if key in processed: continue
            rp = resolve_path(raw)
            if not rp:
                unresolved += 1
                if unresolved <= 50:
                    write_jsonl(UNRESOLVED,{"raw_path":raw,"feed":feed,"feed_name":feed_name,"reason":"cannot_resolve_local_path","timestamp":now()})
                continue
            text = read_text_safe(rp)
            score = get_score(row,text,rp)
            if score in buckets:
                buckets[score].append((rp,row,feed,text,key,raw,feed_name))

        selected_score, batch = None, []
        for s in [5,4,3]:
            if buckets[s]:
                selected_score = s
                batch = buckets[s][:BATCH_PROCESS]
                break

        status = {"mission":"P4.91N5","cycle":cycle,"timestamp":now(),"feed_status":feed_status,"pending_score_5":len(buckets[5]),"pending_score_4":len(buckets[4]),"pending_score_3":len(buckets[3]),"selected_score":selected_score,"selected_batch":len(batch),"processed_total":len(processed),"unresolved_paths":unresolved,"index_count":index_count,"mode":"FAST_INDEX_STREAMING_LOOP"}
        STATUS.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")

        print("="*100, flush=True)
        print("P4.91N5 FAST INDEX STREAMING CONSUMER", flush=True)
        print(json.dumps(status, indent=2, ensure_ascii=False), flush=True)

        if batch:
            process_batch(batch, selected_score)
            time.sleep(3)
        else:
            time.sleep(15)

if __name__ == "__main__":
    main()
