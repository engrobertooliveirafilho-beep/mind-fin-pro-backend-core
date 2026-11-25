import json
from pathlib import Path
from app.p9_genome_explosion_engine.engine import generate_genomes

def evaluate_genome(genome):
    """Create a research candidate only; never fabricate performance metrics."""
    return {
        "genome_id": genome["genome_id"],
        "genome": genome,
        "metrics": None,
        "validation": {
            "walk_forward": "NOT_RUN",
            "monte_carlo": "NOT_RUN",
            "robustness_committee": "NOT_RUN",
            "anti_overfitting": "NOT_RUN",
            "promotion_allowed": False
        },
        "research_score": None,
        "status": "BLOCKED_REAL_BACKTEST_ENGINE_NOT_CONNECTED",
        "edge_proven": False,
        "causality_proven": False,
        "promotion_allowed": False
    }

def run(n=10000, top=250):
    if type(n) is not int or n < 1 or type(top) is not int or top < 1:
        raise ValueError("INVALID_P9_3_BATCH")
    out = Path("reports/P9.3_MASSIVE_BACKTEST_GRID")
    out.mkdir(parents=True, exist_ok=True)
    genomes = generate_genomes(n)
    candidates = [evaluate_genome(g) for g in genomes]
    (out / "P9.3_unvalidated_genomes.json").write_text(
        json.dumps(candidates, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Keep the legacy output path, but never expose untested genomes as ranked results.
    (out / "P9.3_top_ranked_candidates.json").write_text("[]", encoding="utf-8")
    manifest = {
        "STATUS": "P9.3_BLOCKED_REAL_BACKTEST_ENGINE_NOT_CONNECTED",
        "GENOMES_GENERATED": len(genomes),
        "BACKTESTS_EXECUTED": 0,
        "TOP_EXPORTED": 0,
        "LIVE": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "PROMOTION_ALLOWED": False,
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "BLOCKING_GATE": "REAL_MARKET_BACKTEST_EXECUTOR_AND_COST_MODEL_REQUIRED",
        "EXPORT_READY": False
    }
    (out / "P9.3_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
