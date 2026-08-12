from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis


SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return -1.0
    return float(np.dot(a, b) / denom)


def load_face(app: FaceAnalysis, path: Path) -> np.ndarray | None:
    image = cv2.imread(str(path))
    if image is None:
        return None
    faces = app.get(image)
    if len(faces) != 1:
        return None
    return faces[0].normed_embedding


def reference_paths(root: Path) -> list[Path]:
    refs = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        text = str(path).upper()
        if "FACE_LOCK_V1" in text or "MASTER_CANON_15" in text or "MASTER_CANON_10" in text:
            refs.append(path)
    return sorted(refs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--reference-dir", required=True, type=Path)
    parser.add_argument("--report-file", required=True, type=Path)
    parser.add_argument("--threshold", type=float, default=0.42)
    parser.add_argument("--minimum-valid-references", type=int, default=3)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    refs = reference_paths(args.reference_dir)
    if not refs:
        raise RuntimeError("Nenhuma referência facial canônica.")

    if args.check:
        print(json.dumps({
            "status": "READY",
            "reference_candidates": len(refs),
            "threshold": args.threshold,
        }, indent=2))
        return 0

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640))

    candidate = load_face(app, args.candidate)
    if candidate is None:
        payload = {
            "status": "FAIL",
            "reason": "candidate_requires_exactly_one_detected_face",
            "candidate": str(args.candidate),
        }
        args.report_file.parent.mkdir(parents=True, exist_ok=True)
        args.report_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return 2

    scores = []
    invalid = 0
    for ref in refs:
        embedding = load_face(app, ref)
        if embedding is None:
            invalid += 1
            continue
        scores.append({"reference": str(ref), "score": cosine(candidate, embedding)})

    if len(scores) < args.minimum_valid_references:
        raise RuntimeError(
            f"Referências válidas insuficientes: {len(scores)} < {args.minimum_valid_references}"
        )

    values = sorted((item["score"] for item in scores), reverse=True)
    top = values[: min(5, len(values))]
    aggregate = float(np.mean(top))
    status = "PASS" if aggregate >= args.threshold else "FAIL"

    payload = {
        "schema": "eldora.identity.validation.v1",
        "status": status,
        "candidate": str(args.candidate),
        "threshold": args.threshold,
        "aggregate_top5_mean": aggregate,
        "best_score": values[0],
        "valid_references": len(scores),
        "invalid_references": invalid,
        "top_matches": sorted(scores, key=lambda item: item["score"], reverse=True)[:10],
    }
    args.report_file.parent.mkdir(parents=True, exist_ok=True)
    args.report_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if status == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())