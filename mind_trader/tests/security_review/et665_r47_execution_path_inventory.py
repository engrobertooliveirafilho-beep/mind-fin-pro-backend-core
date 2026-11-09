"""ET665.R47: offline, read-only inventory. Findings are review candidates, not proven vulnerabilities."""
import argparse
import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

PATTERNS = {
    "PROCESS_SPAWN": {"subprocess.run", "subprocess.Popen", "subprocess.call", "subprocess.check_call", "subprocess.check_output", "os.system", "os.popen", "os.spawnl", "os.spawnv", "os.execv", "os.execve", "asyncio.create_subprocess_exec", "asyncio.create_subprocess_shell"},
    "MT5_TERMINAL": {"mt5.initialize", "mt5.login", "mt5.order_send", "mt5.order_check", "mt5.positions_get", "MetaTrader5.initialize", "MetaTrader5.order_send"},
    "NETWORK": {"requests.get", "requests.post", "requests.request", "httpx.get", "httpx.post", "httpx.Client", "urllib.request.urlopen", "socket.socket", "websocket.create_connection"},
    "DYNAMIC_EXEC": {"eval", "exec", "compile", "__import__", "importlib.import_module"},
}


def call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = call_name(node.value)
        return base + "." + node.attr if base else node.attr
    return ""


def inventory(root):
    findings = []
    checked = 0
    for path in sorted(root.rglob("*.py")):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        checked += 1
        try:
            tree = ast.parse(data.decode("utf-8-sig"), filename=rel)
        except (SyntaxError, UnicodeError) as exc:
            findings.append({"path": rel, "line": getattr(exc, "lineno", 0) or 0, "category": "PARSE_ERROR", "symbol": type(exc).__name__, "sha256": digest})
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                for name in names:
                    if name == "MetaTrader5" or name.startswith("MetaTrader5."):
                        findings.append({"path": rel, "line": node.lineno, "category": "MT5_IMPORT", "symbol": name, "sha256": digest})
            if isinstance(node, ast.Call):
                symbol = call_name(node.func)
                for category, names in PATTERNS.items():
                    if symbol in names:
                        findings.append({"path": rel, "line": node.lineno, "category": category, "symbol": symbol, "sha256": digest})
    return checked, findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("root does not exist")
    checked, findings = inventory(root)
    args.out.mkdir(parents=True, exist_ok=True)
    fields = ["path", "line", "category", "symbol", "sha256"]
    with (args.out / "R47_FINDINGS.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(findings)
    summary = {"mission": "ET665.R47", "files_scanned": checked, "findings_total": len(findings), "categories": dict(sorted(Counter(x["category"] for x in findings).items())), "interpretation": "static review candidates; not confirmed vulnerabilities", "phase_b": "OPEN", "real_orders": "FORBIDDEN"}
    (args.out / "R47_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
