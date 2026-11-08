"""ET665.R60: offline, read-only, fail-closed Drive/Git manifest reconciliation.

Both inputs must be explicit CSV exports. No Drive or broker access is performed.
Drive manifest: path,sha256,size_bytes; Git manifest: R59 CSV.
Optional mapping CSV: drive_path,git_path; unmapped entries remain unmatched.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

SHA_COLUMNS = {"sha256"}
def load_csv(path, required, key):
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("MISSING_COLUMNS:" + str(path) + ":" + ",".join(sorted(required)))
        result = {}
        for number, row in enumerate(reader, 2):
            k = (row.get(key) or "").replace("\\", "/").strip()
            sha = (row.get("sha256") or "").strip().lower() if "sha256" in required else ""
            if not k or k.startswith("/") or ".." in k.split("/") or (sha and (len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha))):
                raise ValueError("INVALID_RECORD:" + str(path) + ":" + str(number))
            if k in result:
                raise ValueError("DUPLICATE_PATH:" + str(path) + ":" + k)
            result[k] = row
            if sha:
                result[k]["sha256"] = sha
        return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--git-manifest", type=Path, required=True)
    p.add_argument("--drive-manifest", type=Path, required=True)
    p.add_argument("--mapping", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected-git-manifest-sha256", required=True)
    p.add_argument("--expected-drive-manifest-sha256", required=True)
    a = p.parse_args()
    for source in (a.git_manifest, a.drive_manifest):
        if not source.is_file():
            raise SystemExit("INPUT_NOT_FOUND:" + str(source))
    for source, expected in ((a.git_manifest, a.expected_git_manifest_sha256), (a.drive_manifest, a.expected_drive_manifest_sha256)):
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual != expected.lower():
            raise SystemExit("INPUT_SHA256_MISMATCH:" + str(source))
    if a.output.exists():
        raise SystemExit("OUTPUT_ALREADY_EXISTS")
    git = load_csv(a.git_manifest, {"path", "sha256", "size_bytes"}, "path")
    drive = load_csv(a.drive_manifest, {"path", "sha256", "size_bytes"}, "path")
    mapping = {}
    if a.mapping:
        rows = load_csv(a.mapping, {"drive_path", "git_path"}, "drive_path")
        mapping = {k: v["git_path"].replace("\\", "/").strip() for k, v in rows.items()}
        if len(set(mapping.values())) != len(mapping):
            raise SystemExit("AMBIGUOUS_MAPPING")
        if any(not x or x.startswith("/") or ".." in x.split("/") for x in mapping.values()):
            raise SystemExit("INVALID_MAPPING")
    if not git or not drive:
        raise SystemExit("EMPTY_MANIFEST")
    records = []
    used_git = set()
    for dpath, d in sorted(drive.items()):
        gpath = mapping.get(dpath, dpath)
        if gpath in used_git:
            raise SystemExit("AMBIGUOUS_GIT_TARGET:" + gpath)
        used_git.add(gpath)
        g = git.get(gpath)
        if g is None:
            status = "DRIVE_ONLY"
        elif d["sha256"] != g["sha256"] or d["size_bytes"] != g["size_bytes"]:
            status = "CONTENT_MISMATCH"
        else:
            status = "MATCH"
        records.append({"drive_path": dpath, "git_path": gpath, "status": status})
    for gpath in sorted(git.keys() - used_git):
        records.append({"drive_path": "", "git_path": gpath, "status": "GIT_ONLY"})
    counts = {k: sum(r["status"] == k for r in records) for k in ("MATCH", "DRIVE_ONLY", "GIT_ONLY", "CONTENT_MISMATCH")}
    a.output.mkdir(parents=True)
    with (a.output / "RECONCILIATION.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["drive_path", "git_path", "status"])
        w.writeheader()
        w.writerows(records)
    summary = {
        "schema": "ET665_R60_DRIVE_GIT_RECONCILIATION_V1",
        "drive_entries": len(drive), "git_entries": len(git), "counts": counts,
        "mapping_entries": len(mapping),
        "scope": "ONLY_EXPLICITLY_SUPPLIED_MANIFESTS",
        "full_drive_authority_certified": False,
        "semantic_equivalence_certified": False,
        "phase_b": "OPEN", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
        "reconciliation_status": "MATCH" if counts["DRIVE_ONLY"] == counts["GIT_ONLY"] == counts["CONTENT_MISMATCH"] == 0 else "DIFFERENCES",
    }
    (a.output / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["reconciliation_status"] == "MATCH" else 2

if __name__ == "__main__":
    raise SystemExit(main())
