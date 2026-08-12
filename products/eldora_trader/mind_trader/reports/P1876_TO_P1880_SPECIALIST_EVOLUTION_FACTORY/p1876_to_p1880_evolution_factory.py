import json
import hashlib
from pathlib import Path
from datetime import datetime, UTC

BASE = Path("reports/P1876_TO_P1880_SPECIALIST_EVOLUTION_FACTORY")
SPECIALISTS = Path("data/lake/specialists")
EXPERIMENTS = Path("data/lake/experiments")
QUARANTINE = Path("data/lake/quarantine")

PATTERN = Path("data/lake/dna/p1875_pattern_genome.json")
MC = Path("reports/P1809B_MONTE_CARLO_10000_TRADE_SEQUENCE/p1809b_monte_carlo_10000_report.json")

def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

patterns = load_json(PATTERN, [])
mc = load_json(MC, {})
elite_edges = mc.get("APPROVED_EDGES", [])

def stable_id(obj, prefix):
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return prefix + "_" + hashlib.md5(raw.encode()).hexdigest()[:16]

mutation_templates = [
    {
        "mutation_type": "ADD_SESSION_FILTER",
        "params": ["session"]
    },
    {
        "mutation_type": "ADD_VOLATILITY_FILTER",
        "params": ["volatility_regime"]
    },
    {
        "mutation_type": "ADD_TREND_FILTER",
        "params": ["trend_regime"]
    },
    {
        "mutation_type": "ADD_TRIGGER_FILTER",
        "params": ["trigger"]
    },
    {
        "mutation_type": "ADD_SESSION_VOLATILITY_FILTER",
        "params": ["session", "volatility_regime"]
    },
    {
        "mutation_type": "ADD_TREND_VOLATILITY_FILTER",
        "params": ["trend_regime", "volatility_regime"]
    },
    {
        "mutation_type": "ADD_FULL_CONTEXT_FILTER",
        "params": ["session", "trend_regime", "volatility_regime", "trigger"]
    },
    {
        "mutation_type": "STRICT_HIGH_PF_CLUSTER_ONLY",
        "params": ["profit_factor_proxy"]
    },
    {
        "mutation_type": "STRICT_HIGH_WINRATE_CLUSTER_ONLY",
        "params": ["win_rate"]
    },
    {
        "mutation_type": "STRICT_MIN_SAMPLE_FILTER",
        "params": ["trades"]
    }
]

mutations = []
family_tree = []
specialist_genomes = []

for edge in elite_edges:
    parent_asset = edge["asset"]
    parent_family = edge["family"]
    parent_id = edge["edge_id"]

    related_patterns = [
        p for p in patterns
        if p.get("asset") == parent_asset and p.get("family") == parent_family
    ]

    for p in related_patterns:
        for t in mutation_templates:
            genome = p.get("genome", {})
            evidence = p.get("evidence", {})

            child = {
                "parent_edge_id": parent_id,
                "parent_asset": parent_asset,
                "parent_timeframe": edge["timeframe"],
                "parent_family": parent_family,
                "source_pattern_id": p.get("pattern_id"),
                "mutation_type": t["mutation_type"],
                "filters": {k: genome.get(k) for k in t["params"] if k in genome},
                "thresholds": {
                    "min_pf": 1.20,
                    "min_win_rate": 0.50,
                    "min_trades": 20,
                    "require_10y": True,
                    "require_walk_forward": True,
                    "require_mc_10k": True
                },
                "source_evidence": evidence,
                "mode": "RESEARCH_ONLY",
                "ORDER_SENT": False,
                "REAL_ORDERS": "FORBIDDEN",
                "FTMO_REAL": "FORBIDDEN",
                "MT5_REAL": "FORBIDDEN"
            }

            child_id = stable_id(child, "MUT")
            child["mutation_id"] = child_id
            child["specialist_id"] = f"{parent_asset}_{edge['timeframe']}_{parent_family}_{child_id}"

            mutations.append(child)

            family_tree.append({
                "parent_edge_id": parent_id,
                "child_specialist_id": child["specialist_id"],
                "generation": 1,
                "mutation_type": t["mutation_type"],
                "source_pattern_id": p.get("pattern_id"),
                "validation_status": "PENDING_BACKTEST",
                "created_at": datetime.now(UTC).isoformat()
            })

            specialist_genomes.append({
                "specialist_id": child["specialist_id"],
                "asset": parent_asset,
                "timeframe": edge["timeframe"],
                "family": parent_family,
                "generation": 1,
                "genome": {
                    "base_family": parent_family,
                    "pattern_genome": genome,
                    "mutation": t["mutation_type"],
                    "filters": child["filters"],
                    "evidence": evidence
                },
                "status": "PENDING_VALIDATION",
                "mode": "RESEARCH_ONLY",
                "ORDER_SENT": False,
                "REAL_ORDERS": "FORBIDDEN",
                "FTMO_REAL": "FORBIDDEN",
                "MT5_REAL": "FORBIDDEN"
            })

# Crossover: mistura genomas XAU e USDJPY apenas como hipótese, sem validação automática
crossovers = []
xau_patterns = [p for p in patterns if p.get("asset") == "XAUUSD"]
jpy_patterns = [p for p in patterns if p.get("asset") == "USDJPY"]

for xp in xau_patterns[:10]:
    for jp in jpy_patterns[:10]:
        crossover = {
            "type": "GENETIC_CROSSOVER",
            "parents": [xp.get("pattern_id"), jp.get("pattern_id")],
            "source_assets": ["XAUUSD", "USDJPY"],
            "hypothesis": "Combine liquidity/sweep context with statistical reversion context",
            "genome": {
                "xau_component": xp.get("genome"),
                "jpy_component": jp.get("genome")
            },
            "status": "HYPOTHESIS_ONLY_PENDING_BACKTEST",
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN"
        }
        crossover["crossover_id"] = stable_id(crossover, "XOV")
        crossovers.append(crossover)

# Survival prefilter: não aprova, só prioriza experimentos com evidência melhor
survivors = []
quarantined = []

for m in mutations:
    ev = m.get("source_evidence", {})
    pf = float(ev.get("profit_factor_proxy") or 0)
    wr = float(ev.get("win_rate") or 0)
    trades = int(ev.get("trades") or 0)

    score = pf * 35 + wr * 30 + min(trades, 100) * 0.35

    row = {
        "mutation_id": m["mutation_id"],
        "specialist_id": m["specialist_id"],
        "parent_edge_id": m["parent_edge_id"],
        "asset": m["parent_asset"],
        "family": m["parent_family"],
        "mutation_type": m["mutation_type"],
        "pre_survival_score": round(score, 6),
        "pf_proxy": pf,
        "win_rate": wr,
        "trades": trades,
        "status": "PRIORITY_BACKTEST" if score >= 75 and trades >= 5 else "QUARANTINE_PREFILTER",
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN"
    }

    if row["status"] == "PRIORITY_BACKTEST":
        survivors.append(row)
    else:
        quarantined.append(row)

mutations_file = SPECIALISTS / "p1876_elite_mutations.json"
crossovers_file = SPECIALISTS / "p1877_genetic_crossovers.json"
survivors_file = SPECIALISTS / "p1878_survival_prefilter.json"
family_file = SPECIALISTS / "p1879_family_tree.json"
genome_file = SPECIALISTS / "p1880_specialist_genomes.json"
quarantine_file = QUARANTINE / "p1878_quarantine_prefilter.json"

mutations_file.write_text(json.dumps(mutations, indent=2, ensure_ascii=False), encoding="utf-8")
crossovers_file.write_text(json.dumps(crossovers, indent=2, ensure_ascii=False), encoding="utf-8")
survivors_file.write_text(json.dumps(survivors, indent=2, ensure_ascii=False), encoding="utf-8")
family_file.write_text(json.dumps(family_tree, indent=2, ensure_ascii=False), encoding="utf-8")
genome_file.write_text(json.dumps(specialist_genomes, indent=2, ensure_ascii=False), encoding="utf-8")
quarantine_file.write_text(json.dumps(quarantined, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1876_TO_P1880_SPECIALIST_EVOLUTION_FACTORY_COMPLETED",
    "P1876_MUTATIONS_CREATED": len(mutations),
    "P1877_CROSSOVERS_CREATED": len(crossovers),
    "P1878_PRIORITY_SURVIVORS": len(survivors),
    "P1878_QUARANTINED_PREFILTER": len(quarantined),
    "P1879_FAMILY_TREE_ROWS": len(family_tree),
    "P1880_SPECIALIST_GENOMES": len(specialist_genomes),
    "OUTPUTS": {
        "mutations": str(mutations_file),
        "crossovers": str(crossovers_file),
        "survivors": str(survivors_file),
        "family_tree": str(family_file),
        "specialist_genomes": str(genome_file),
        "quarantine": str(quarantine_file)
    },
    "NEXT": "P1881_TO_P1885_ASSET_PERSONALITY_FACTORY",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(BASE / "p1876_to_p1880_specialist_evolution_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
