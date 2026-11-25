import hashlib
import json
import re
from pathlib import Path

SOURCE_TYPES = ["book", "paper", "whitepaper", "note", "internal_material"]
DNA_TAGS = ["trend", "mean_reversion", "breakout", "volatility", "liquidity", "risk", "execution", "psychology", "regime", "macro", "microstructure"]


def _validate_source(text, source_type, title):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("REAL_KNOWLEDGE_SOURCE_REQUIRED")
    if source_type not in SOURCE_TYPES:
        raise ValueError("UNSUPPORTED_SOURCE_TYPE")
    if not isinstance(title, str) or not title.strip() or len(title) > 512:
        raise ValueError("INVALID_SOURCE_TITLE")
    return text.strip(), source_type, title.strip()


def source_id(text, source_type):
    if not isinstance(text, str) or not isinstance(source_type, str):
        raise ValueError("INVALID_SOURCE_ID_INPUT")
    return hashlib.sha256((source_type + "\0" + text).encode("utf-8")).hexdigest()


def extract_dna(text, source_type="note", title="untitled"):
    text, source_type, title = _validate_source(text, source_type, title)
    normalized = text.casefold()
    full_source_hash = source_id(text, source_type)
    tags = []
    for tag in DNA_TAGS:
        phrase = tag.replace("_", " ")
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", normalized):
            tags.append(tag)
    if not tags:
        tags = ["unclassified_research"]

    candidates = []
    for tag in tags:
        dna_id = hashlib.sha256((full_source_hash + "\0" + title + "\0" + tag).encode("utf-8")).hexdigest()[:24]
        candidates.append({
            "dna_id": dna_id,
            "source_id": full_source_hash,
            "source_sha256": full_source_hash,
            "source_title": title,
            "source_type": source_type,
            "tag": tag,
            "hypothesis": f"{tag} keyword candidate extracted from supplied source; semantic validation required",
            "extraction_method": "BOUNDED_KEYWORD_TAGGING",
            "status": "DNA_CANDIDATE_NOT_VALIDATED",
            "edge_assumed": False,
            "causality_assumed": False,
            "promotion_allowed": False,
        })
    return {
        "source_id": full_source_hash,
        "source_sha256": full_source_hash,
        "title": title,
        "source_type": source_type,
        "content_chars": len(text),
        "extraction_method": "BOUNDED_KEYWORD_TAGGING",
        "dna_candidates": candidates,
    }


def dna_to_genome_candidates(dna):
    if not isinstance(dna, dict) or not isinstance(dna.get("dna_candidates"), list):
        raise ValueError("INVALID_DNA_PAYLOAD")
    source_hash = dna.get("source_sha256")
    if not isinstance(source_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", source_hash):
        raise ValueError("SOURCE_PROVENANCE_REQUIRED")
    out = []
    for candidate in dna["dna_candidates"]:
        if candidate.get("source_sha256") != source_hash:
            raise ValueError("DNA_SOURCE_PROVENANCE_MISMATCH")
        out.append({
            "genome_candidate_id": hashlib.sha256((candidate["dna_id"] + ":genome").encode("utf-8")).hexdigest()[:24],
            "dna_id": candidate["dna_id"],
            "source_id": dna["source_id"],
            "source_sha256": source_hash,
            "family": candidate["tag"],
            "origin": "KNOWLEDGE_DNA_UNVALIDATED",
            "requires_backtest": True,
            "requires_walk_forward": True,
            "requires_monte_carlo": True,
            "requires_robustness_committee": True,
            "live_allowed": False,
            "promotion_allowed": False,
        })
    return out


def run(sample_text=None, source_type="note", title=None):
    out = Path("reports/P9.4_DNA_EXTRACTION_ENGINE")
    out.mkdir(parents=True, exist_ok=True)
    if sample_text is None or not isinstance(sample_text, str) or not sample_text.strip():
        dna = {"source_id": None, "source_sha256": None, "title": None, "source_type": None, "content_chars": 0, "extraction_method": None, "dna_candidates": []}
        genome_candidates = []
        manifest = {
            "STATUS": "P9.4_BLOCKED_SOURCE_REQUIRED",
            "SOURCES_SUPPORTED": SOURCE_TYPES,
            "DNA_CANDIDATES": 0,
            "GENOME_CANDIDATES": 0,
            "SOURCE_PROVENANCE": "MISSING",
            "EDGE": "NOT_PROVEN",
            "CAUSALITY": "NOT_PROVEN",
            "LIVE": "FORBIDDEN",
            "REAL_BROKER": "DISABLED",
            "PROMOTION_ALLOWED": False,
            "EXPORT_READY": False,
        }
    else:
        dna = extract_dna(sample_text, source_type, title or "untitled")
        genome_candidates = dna_to_genome_candidates(dna)
        manifest = {
            "STATUS": "P9.4_CANDIDATES_EXTRACTED_UNVALIDATED",
            "SOURCES_SUPPORTED": SOURCE_TYPES,
            "DNA_CANDIDATES": len(dna["dna_candidates"]),
            "GENOME_CANDIDATES": len(genome_candidates),
            "SOURCE_PROVENANCE": "SHA256_RECORDED",
            "EXTRACTION_METHOD": "BOUNDED_KEYWORD_TAGGING",
            "EDGE": "NOT_PROVEN",
            "CAUSALITY": "NOT_PROVEN",
            "LIVE": "FORBIDDEN",
            "REAL_BROKER": "DISABLED",
            "PROMOTION_ALLOWED": False,
            "EXPORT_READY": False,
        }
    (out / "P9.4_dna_candidates.json").write_text(json.dumps(dna, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "P9.4_genome_candidates_from_dna.json").write_text(json.dumps(genome_candidates, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "P9.4_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
