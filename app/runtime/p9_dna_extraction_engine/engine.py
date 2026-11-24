import json, hashlib, re
from pathlib import Path

SOURCE_TYPES=["book","paper","whitepaper","note","internal_material"]
DNA_TAGS=["trend","mean_reversion","breakout","volatility","liquidity","risk","execution","psychology","regime","macro","microstructure"]

def source_id(text, source_type):
    return hashlib.sha256(json.dumps([source_type,text],ensure_ascii=False).encode("utf-8")).hexdigest()

def extract_dna(text, source_type="note", title="untitled"):
    if source_type not in SOURCE_TYPES:
        raise ValueError("unsupported source type")
    if not isinstance(text,str) or not text.strip():
        raise ValueError("nonempty source text required")
    t=text.lower()
    tags=[x for x in DNA_TAGS if x.replace("_"," ") in t or x in t]
    if not tags: tags=["unclassified_research"]
    candidates=[]
    for tag in tags:
        candidates.append({
            "dna_id":hashlib.sha256(json.dumps([title,tag,source_id(text,source_type)],ensure_ascii=False).encode("utf-8")).hexdigest(),
            "source_title":title,
            "source_id":source_id(text,source_type),
            "extraction_method":"KEYWORD_ONLY",
            "source_type":source_type,
            "tag":tag,
            "hypothesis":f"{tag} candidate extracted from knowledge source",
            "status":"DNA_CANDIDATE_NOT_VALIDATED",
            "edge_assumed":False,
            "causality_assumed":False,
            "promotion_allowed":False
        })
    return {"source_id":source_id(text,source_type),"title":title,"source_type":source_type,"dna_candidates":candidates}

def dna_to_genome_candidates(dna):
    out=[]
    for c in dna["dna_candidates"]:
        out.append({
            "genome_candidate_id":hashlib.sha256((c["dna_id"]+":genome").encode()).hexdigest()[:18],
            "dna_id":c["dna_id"],
            "family":c["tag"],
            "origin":"KNOWLEDGE_DNA",
            "requires_backtest":True,
            "requires_walk_forward":True,
            "requires_monte_carlo":True,
            "requires_robustness_committee":True,
            "live_allowed":False,
            "promotion_allowed":False
        })
    return out

def run(sample_text=None):
    out=Path("reports/P9.4_DNA_EXTRACTION_ENGINE"); out.mkdir(parents=True,exist_ok=True)
    if not isinstance(sample_text,str) or not sample_text.strip():
        raise ValueError("explicit source text required")
    dna=extract_dna(sample_text,"internal_material","P9_seed_research")
    genome_candidates=dna_to_genome_candidates(dna)
    manifest={
        "STATUS":"P9.4_DNA_EXTRACTION_ENGINE_IMPLEMENTED",
        "SOURCES_SUPPORTED":SOURCE_TYPES,
        "DNA_CANDIDATES":len(dna["dna_candidates"]),
        "GENOME_CANDIDATES":len(genome_candidates),
        "EDGE":"NOT_ASSUMED",
        "CAUSALITY":"NOT_ASSUMED",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EXPORT_READY":True
    }
    (out/"P9.4_dna_candidates.json").write_text(json.dumps(dna,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.4_genome_candidates_from_dna.json").write_text(json.dumps(genome_candidates,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.4_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("source",type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.source.read_text(encoding="utf-8")),indent=2,ensure_ascii=False))
