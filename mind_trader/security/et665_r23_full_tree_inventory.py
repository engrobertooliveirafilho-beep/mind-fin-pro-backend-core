"""ET665 R23: read-only, fail-closed inventory of every tracked Python file at HEAD.

No imports from scanned files, no network, no broker, no Drive mutation.
Use a full git object database; sparse working trees are supported.
"""
import argparse
import ast
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

SENSITIVE = {
    "mt5": ("MetaTrader5", "mt5"),
    "process": ("subprocess", "os.system", "os.popen", "os.spawn", "os.exec", "os.fork", "pty.spawn"),
    "network": ("requests", "httpx", "urllib", "aiohttp", "socket", "websocket", "websockets", "ftplib", "paramiko", "boto3"),
    "dynamic": ("eval", "exec", "compile", "__import__", "importlib.import_module", "getattr"),
    "filesystem": ("shutil.rmtree", "os.remove", "os.unlink", "Path.unlink", "Path.write_text", "Path.write_bytes"),
}
PATTERNS = (
    (re.compile(r"\border_send\s*\("), "ORDER_SEND_TOKEN"),
    (re.compile(r"\border_check\s*\("), "ORDER_CHECK_TOKEN"),
    (re.compile(r"\brclone\b", re.I), "RCLONE_TOKEN"),
    (re.compile(r"\b(shell\s*=\s*True)\b"), "SHELL_TRUE_TOKEN"),
    (re.compile(r"\bMetaTrader5\b"), "MT5_TOKEN"),
    (re.compile(r"\b(?:https?://|wss?://)"), "URL_TOKEN"),
)
def git(root, *args, data=None):
    p = subprocess.run(["git", "-C", str(root), *args], input=data,
                       capture_output=True, check=True)
    return p.stdout

def name_of(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        x = name_of(node.value)
        return x + "." + node.attr if x else node.attr
    return ""

def classify(source, path, oid):
    result = {"path": path, "blob": oid, "sha256": hashlib.sha256(source).hexdigest(),
              "parse": "PASS", "hits": [], "imports": [], "entrypoints": []}
    text = source.decode("utf-8-sig", errors="replace")
    try:
        tree = ast.parse(text, filename=path)
    except (SyntaxError, ValueError) as exc:
        result["parse"] = "FAIL:" + type(exc).__name__
        result["hits"].append({"line": getattr(exc, "lineno", 0) or 0, "kind": "AST_PARSE_FAILURE", "expr": str(exc)[:160]})
        tree = None
    if tree is not None:
        aliases = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    aliases[a.asname or a.name.split(".")[0]] = a.name
                    result["imports"].append(a.name)
            elif isinstance(n, ast.ImportFrom):
                module = n.module or ""
                result["imports"].append("." * n.level + module)
                for a in n.names:
                    aliases[a.asname or a.name] = module + "." + a.name
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                raw = name_of(n.func)
                head, sep, rest = raw.partition(".")
                resolved = aliases.get(head, head) + (sep + rest if sep else "")
                categories = [k for k, prefixes in SENSITIVE.items()
                              if any(resolved == prefix or resolved.startswith(prefix + ".") for prefix in prefixes)]
                if categories:
                    result["hits"].append({"line": n.lineno, "kind": "AST_CALL:" + ",".join(categories), "expr": resolved})
                if resolved in ("subprocess.run", "subprocess.Popen", "subprocess.call", "subprocess.check_call",
                                "subprocess.check_output"):
                    shell = next((x.value.value for x in n.keywords if x.arg == "shell"
                                  and isinstance(x.value, ast.Constant)), None)
                    result["hits"].append({"line": n.lineno, "kind": "PROCESS_INVOCATION", "expr": resolved + ";shell=" + str(shell)})
            elif isinstance(n, ast.If) and isinstance(n.test, ast.Compare):
                if "__name__" in ast.unparse(n.test):
                    result["entrypoints"].append(n.lineno)
    for lineno, line in enumerate(text.splitlines(), 1):
        for pattern, kind in PATTERNS:
            if pattern.search(line):
                result["hits"].append({"line": lineno, "kind": kind, "expr": line.strip()[:160]})
    result["imports"] = sorted(set(result["imports"]))
    result["entrypoints"] = sorted(set(result["entrypoints"]))
    result["hits"].sort(key=lambda x: (x["line"], x["kind"], x["expr"]))
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    root = Path(args.repo).resolve()
    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit("OUTPUT_ALREADY_EXISTS")
    head = git(root, "rev-parse", "HEAD").decode().strip()
    entries = git(root, "ls-tree", "-r", "-z", "--full-tree", "HEAD").split(b"\0")
    paths = []
    for entry in entries:
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, typ, oid = metadata.decode().split()
        if typ == "blob" and raw_path.endswith(b".py"):
            paths.append((raw_path.decode("utf-8", "surrogateescape"), oid))
    if not paths:
        raise SystemExit("NO_PYTHON_FILES")
    # One Git batch session avoids process-per-file and supports sparse checkouts.
    proc = subprocess.Popen(["git", "-C", str(root), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for _, oid in paths:
            proc.stdin.write((oid + "\n").encode())
        proc.stdin.close()
        records = []
        for path, oid in paths:
            header = proc.stdout.readline().decode().strip().split()
            if len(header) != 3 or header[0] != oid or header[1] != "blob":
                raise RuntimeError("GIT_BLOB_HEADER_MISMATCH:" + path)
            size = int(header[2])
            source = proc.stdout.read(size)
            if len(source) != size or proc.stdout.read(1) != b"\n":
                raise RuntimeError("GIT_BLOB_TRUNCATED:" + path)
            records.append(classify(source, path, oid))
        if proc.wait(timeout=30):
            raise RuntimeError("GIT_BATCH_FAILED")
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    flagged = [x for x in records if x["hits"]]
    parse_failed = [x["path"] for x in records if x["parse"] != "PASS"]
    result = {
        "schema": "ET665_R23_READ_ONLY_INVENTORY_V1", "head": head,
        "tracked_python_files": len(paths), "analyzed_python_files": len(records),
        "flagged_python_files": len(flagged),
        "total_occurrences": sum(len(x["hits"]) for x in records),
        "ast_parse_failures": parse_failed,
        "inventory_coverage": "COMPLETE_TRACKED_PYTHON" if len(paths) == len(records) else "INCOMPLETE",
        "semantic_security_approval": "NOT_CERTIFIED",
        "phase_b": "BLOCKED", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        "records": records,
    }
    out.mkdir(parents=True)
    (out / "inventory.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "occurrences.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "blob", "sha256", "line", "kind", "expr"])
        for record in records:
            for hit in record["hits"]:
                writer.writerow([record["path"], record["blob"], record["sha256"],
                                 hit["line"], hit["kind"], hit["expr"]])
    summary = {k: v for k, v in result.items() if k != "records"}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for file in ("inventory.json", "occurrences.csv", "summary.json"):
        p = out / file
        print(file + "_SHA256=" + hashlib.sha256(p.read_bytes()).hexdigest())
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if not parse_failed else 2

if __name__ == "__main__":
    sys.exit(main())
