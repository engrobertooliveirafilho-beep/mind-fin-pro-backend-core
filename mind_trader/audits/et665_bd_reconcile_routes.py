"""ET665.BD: offline, read-only reconciliation of operator route inventory.

This tool NEVER imports scanned modules or executes trading code.
It produces a review queue; no keyword match is automatically cleared.
Usage:
 python mind_trader/audits/et665_bd_reconcile_routes.py EXECUTION_ROUTES.csv --root . --out audit_output
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def locate_column(fields, *terms):
    for field in fields:
        key = field.strip().lower().replace("_", "").replace(" ", "")
        if any(term in key for term in terms):
            return field
    return None


def reconcile(csv_path, root, out):
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("Missing CSV headers")
        rows = list(reader)
        fields = reader.fieldnames
    path_col = locate_column(fields, "path", "file")
    line_col = locate_column(fields, "line", "lineno")
    if not path_col:
        raise ValueError("No path/file column; inspect CSV schema before proceeding")
    out.mkdir(parents=True, exist_ok=True)
    queue = []
    for index, row in enumerate(rows, 1):
        raw = (row.get(path_col) or "").strip().replace("\\", "/")
        # Absolute paths and traversal are never read.
        relative = Path(raw)
        if not raw or relative.is_absolute() or ".." in relative.parts or ":" in raw:
            queue.append({"index": index, "path": raw, "status": "INVALID_PATH", "disposition": "REVIEW_REQUIRED"})
            continue
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            queue.append({"index": index, "path": raw, "status": "FILE_NOT_FOUND", "disposition": "REVIEW_REQUIRED"})
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        try:
            line_no = int((row.get(line_col) or "").strip()) if line_col else 0
        except ValueError:
            line_no = 0
        excerpt = lines[line_no - 1].strip()[:240] if 1 <= line_no <= len(lines) else ""
        queue.append({
            "index": index, "path": raw, "line": line_no,
            "source_sha256": sha256(path), "excerpt": excerpt,
            "status": "SOURCE_FOUND" if excerpt else "LINE_UNRESOLVED",
            "disposition": "REVIEW_REQUIRED",
            "import_side_effects": "NOT_REVIEWED",
            "broker_network_reachability": "NOT_REVIEWED",
            "live_lock_enforcement": "NOT_REVIEWED",
        })
    report = {
        "mission": "ET665.BD", "source_csv_sha256": sha256(csv_path),
        "input_rows": len(rows), "source_found": sum(x["status"] == "SOURCE_FOUND" for x in queue),
        "review_required": len(queue), "security_approved": False,
        "phase_b": "OPEN", "real_orders": "FORBIDDEN",
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (out / "review_queue.csv").open("w", newline="", encoding="utf-8") as handle:
        fields_out = ["index", "path", "line", "source_sha256", "excerpt", "status", "disposition",
                      "import_side_effects", "broker_network_reachability", "live_lock_enforcement"]
        writer = csv.DictWriter(handle, fieldnames=fields_out, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(queue)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("ET665_BD_RESULTS"))
    args = parser.parse_args()
    reconcile(args.csv, args.root, args.out)
