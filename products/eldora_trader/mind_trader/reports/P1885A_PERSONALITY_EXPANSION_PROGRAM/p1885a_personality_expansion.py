import json
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

BASE = Path("reports/P1885A_PERSONALITY_EXPANSION_PROGRAM")
OUT = Path("data/lake/personality_expansion")
GEN2 = Path("data/lake/specialists/gen2")
ASSETS = Path("data/lake/assets/expanded")
EXP = Path("data/lake/experiments/p1885a")

SURVIVORS = Path("data/lake/specialists/p1878_survival_prefilter.json")
MUTATIONS = Path("data/lake/specialists/p1876_elite_mutations.json")
DNA = Path("data/lake/dna/p1871_trade_dna.csv")
CLUSTERS = Path("data/lake/dna/p1874_dna_clusters.json")
PATTERNS = Path("data/lake/dna/p1875_pattern_genome.json")
ASSET_PROFILE = Path("data/lake/assets/p1881_to_p1883_asset_personalities.json")

def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def stable_id(obj, prefix):
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return prefix + "_" + hashlib.md5(raw.encode()).hexdigest()[:16]

survivors = load_json(SURVIVORS, [])
mutations = load_json(MUTATIONS, [])
clusters = load_json(CLUSTERS, [])
patterns = load_json(PATTERNS, [])
asset_profiles = load_json(ASSET_PROFILE, [])

dna = pd.read_csv(DNA)

mutation_map = {m["mutation_id"]: m for m in mutations if "mutation_id" in m}

validated = []
promoted = []
rejected = []

for s in survivors:
    mid = s.get("mutation_id")
    m = mutation_map.get(mid)
    if not m:
        continue

    asset = s.get("asset")
    family = s.get("family")
    filters = m.get("filters", {})

    g = dna[(dna["asset"] == asset) & (dna["family"] == family)].copy()

    for k, v in filters.items():
        if k in g.columns and v is not None:
            g = g[g[k].astype(str) == str(v)]

    if len(g) < 5:
        status = "REJECTED_LOW_SAMPLE"
        metrics = {
            "trades": int(len(g)),
            "win_rate": 0,
            "profit_factor_proxy": 0,
            "avg_return": 0,
            "wf_proxy_pass": False,
            "mc_proxy_pass": False,
            "stress_proxy_pass": False
        }
    else:
        wins = g[g["outcome"] == "WIN"]
        losses = g[g["outcome"] == "LOSS"]

        gross_win = float(wins["return_1bar"].sum()) if len(wins) else 0
        gross_loss = abs(float(losses["return_1bar"].sum())) if len(losses) else 0
        pf = gross_win / gross_loss if gross_loss > 0 else gross_win
        wr = len(wins) / len(g)
        avg_ret = float(g["return_1bar"].mean())

        by_year = []
        g["year"] = pd.to_datetime(g["entry_time"], errors="coerce", utc=True).dt.year
        for y, yg in g.groupby("year"):
            if pd.isna(y):
                continue
            yret = float(yg["return_1bar"].sum())
            by_year.append({"year": int(y), "return": yret, "positive": yret > 0, "trades": int(len(yg))})

        years = len(by_year)
        pos_years = len([x for x in by_year if x["positive"]])
        consistency = pos_years / years if years else 0

        wf_pass = years >= 5 and consistency >= 0.60
        mc_pass = pf >= 1.20 and wr >= 0.50 and avg_ret > 0
        stress_pass = pf >= 1.30 and avg_ret > 0

        metrics = {
            "trades": int(len(g)),
            "wins": int(len(wins)),
            "losses": int(len(losses)),
            "win_rate": round(wr, 6),
            "profit_factor_proxy": round(pf, 6),
            "avg_return": round(avg_ret, 8),
            "yearly_consistency_proxy": round(consistency, 6),
            "positive_years_proxy": pos_years,
            "tested_years_proxy": years,
            "wf_proxy_pass": wf_pass,
            "mc_proxy_pass": mc_pass,
            "stress_proxy_pass": stress_pass,
            "yearly_proxy": by_year
        }

        status = "GEN2_ELITE_PROMOTED" if (
            pf >= 1.30 and wr >= 0.50 and avg_ret > 0 and wf_pass and mc_pass and stress_pass
        ) else "REJECTED_VALIDATION"

    row = {
        "specialist_id": s.get("specialist_id"),
        "mutation_id": mid,
        "parent_edge_id": s.get("parent_edge_id"),
        "asset": asset,
        "family": family,
        "mutation_type": s.get("mutation_type"),
        "filters": filters,
        "validation_metrics": metrics,
        "status": status,
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }

    validated.append(row)

    if status == "GEN2_ELITE_PROMOTED":
        promoted.append(row)
    else:
        rejected.append(row)

# Personality discovery from promoted GEN2
personalities = []
for asset, rows in pd.DataFrame(promoted).groupby("asset") if promoted else []:
    asset_promoted = rows.to_dict("records")

    dna_asset = dna[dna["asset"] == asset].copy()
    personality_clusters = []

    for p in asset_promoted:
        filters = p.get("filters", {})
        g = dna_asset.copy()
        for k, v in filters.items():
            if k in g.columns and v is not None:
                g = g[g[k].astype(str) == str(v)]

        if len(g) == 0:
            continue

        wins = g[g["outcome"] == "WIN"]
        losses = g[g["outcome"] == "LOSS"]
        gross_win = float(wins["return_1bar"].sum()) if len(wins) else 0
        gross_loss = abs(float(losses["return_1bar"].sum())) if len(losses) else 0
        pf = gross_win / gross_loss if gross_loss > 0 else gross_win

        personality_clusters.append({
            "specialist_id": p["specialist_id"],
            "mutation_type": p["mutation_type"],
            "filters": filters,
            "trades": int(len(g)),
            "win_rate": round(len(wins)/len(g), 6),
            "profit_factor_proxy": round(pf, 6),
            "avg_return": round(float(g["return_1bar"].mean()), 8),
            "personality_label": f"{asset}_{p['mutation_type']}"
        })

    personality_clusters = sorted(
        personality_clusters,
        key=lambda x: (x["profit_factor_proxy"], x["win_rate"], x["trades"]),
        reverse=True
    )

    personalities.append({
        "asset": asset,
        "status": "P1885A_PERSONALITY_DISCOVERY_COMPLETED",
        "gen2_elites": len(asset_promoted),
        "personality_clusters": personality_clusters[:50],
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN"
    })

# Transfer learning queue
target_assets = ["EURUSD","GBPUSD","USDCAD","AUDUSD","XAUUSD","USDJPY"]
transfer_queue = []

for p in promoted:
    for target in target_assets:
        if target == p["asset"]:
            continue

        transfer = {
            "source_specialist_id": p["specialist_id"],
            "source_asset": p["asset"],
            "target_asset": target,
            "family": p["family"],
            "mutation_type": p["mutation_type"],
            "filters_to_transfer": p["filters"],
            "status": "PENDING_TARGET_ASSET_10Y_BACKTEST",
            "rule": "TRANSFER_GENOME_NOT_PERFORMANCE_ASSUMPTION",
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN"
        }
        transfer["transfer_id"] = stable_id(transfer, "TRN")
        transfer_queue.append(transfer)

# Ranking
ranking = []
for p in promoted:
    m = p["validation_metrics"]
    score = (
        float(m.get("profit_factor_proxy", 0)) * 30 +
        float(m.get("win_rate", 0)) * 25 +
        float(m.get("yearly_consistency_proxy", 0)) * 25 +
        min(int(m.get("trades", 0)), 100) * 0.20
    )

    tier = "S+"
    if score < 120:
        tier = "S"
    if score < 90:
        tier = "A"
    if score < 70:
        tier = "B"

    ranking.append({
        "specialist_id": p["specialist_id"],
        "asset": p["asset"],
        "family": p["family"],
        "mutation_type": p["mutation_type"],
        "score": round(score, 6),
        "tier": tier,
        "metrics": m,
        "status": "RANKED_GEN2_ELITE"
    })

ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)

validated_file = EXP / "p1885a_validated_mutations.json"
promoted_file = GEN2 / "p1885a_gen2_elites.json"
rejected_file = EXP / "p1885a_rejected_mutations.json"
personalities_file = ASSETS / "p1885a_expanded_personality_library.json"
transfer_file = EXP / "p1885a_cross_asset_transfer_queue.json"
ranking_file = GEN2 / "p1885a_gen2_ranking.json"

validated_file.write_text(json.dumps(validated, indent=2, ensure_ascii=False), encoding="utf-8")
promoted_file.write_text(json.dumps(promoted, indent=2, ensure_ascii=False), encoding="utf-8")
rejected_file.write_text(json.dumps(rejected, indent=2, ensure_ascii=False), encoding="utf-8")
personalities_file.write_text(json.dumps(personalities, indent=2, ensure_ascii=False), encoding="utf-8")
transfer_file.write_text(json.dumps(transfer_queue, indent=2, ensure_ascii=False), encoding="utf-8")
ranking_file.write_text(json.dumps(ranking, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1885A_PERSONALITY_EXPANSION_PROGRAM_COMPLETED",
    "SURVIVORS_INPUT": len(survivors),
    "MUTATIONS_VALIDATED": len(validated),
    "GEN2_ELITES_PROMOTED": len(promoted),
    "REJECTED": len(rejected),
    "EXPANDED_PERSONALITIES": len(personalities),
    "CROSS_ASSET_TRANSFER_JOBS": len(transfer_queue),
    "RANKED_GEN2": len(ranking),
    "TOP20_GEN2": ranking[:20],
    "OUTPUTS": {
        "validated": str(validated_file),
        "promoted_gen2": str(promoted_file),
        "rejected": str(rejected_file),
        "expanded_personalities": str(personalities_file),
        "transfer_queue": str(transfer_file),
        "ranking": str(ranking_file)
    },
    "NEXT": "P1886_TO_P1890_MARKET_MEMORY_FACTORY",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(BASE / "p1885a_personality_expansion_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
