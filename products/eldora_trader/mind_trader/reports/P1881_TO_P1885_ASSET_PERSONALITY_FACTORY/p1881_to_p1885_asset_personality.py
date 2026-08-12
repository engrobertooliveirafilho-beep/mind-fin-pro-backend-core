import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

BASE = Path("reports/P1881_TO_P1885_ASSET_PERSONALITY_FACTORY")
ASSETS = Path("data/lake/assets")
MEMORY = Path("data/lake/memory")

TRADE_DNA = Path("data/lake/dna/p1871_trade_dna.csv")
CLUSTERS = Path("data/lake/dna/p1874_dna_clusters.json")
PATTERNS = Path("data/lake/dna/p1875_pattern_genome.json")
SURVIVORS = Path("data/lake/specialists/p1878_survival_prefilter.json")
MUTATIONS = Path("data/lake/specialists/p1876_elite_mutations.json")

def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

clusters = load_json(CLUSTERS, [])
patterns = load_json(PATTERNS, [])
survivors = load_json(SURVIVORS, [])
mutations = load_json(MUTATIONS, [])

df = pd.read_csv(TRADE_DNA)

asset_profiles = []
asset_genome_library = []
cross_asset_rows = []
memory_rows = []

for asset, g in df.groupby("asset"):
    total = len(g)
    wins = g[g["outcome"] == "WIN"]
    losses = g[g["outcome"] == "LOSS"]

    wr = len(wins) / total if total else 0
    avg_ret = float(g["return_1bar"].mean()) if total else 0
    gross_win = float(wins["return_1bar"].sum()) if len(wins) else 0
    gross_loss = abs(float(losses["return_1bar"].sum())) if len(losses) else 0
    pf = gross_win / gross_loss if gross_loss > 0 else gross_win

    session_stats = []
    for session, sg in g.groupby("session"):
        sw = sg[sg["outcome"] == "WIN"]
        sl = sg[sg["outcome"] == "LOSS"]
        s_pf = float(sw["return_1bar"].sum()) / abs(float(sl["return_1bar"].sum())) if len(sl) and abs(float(sl["return_1bar"].sum())) > 0 else float(sw["return_1bar"].sum())
        session_stats.append({
            "session": session,
            "trades": int(len(sg)),
            "win_rate": round(len(sw)/len(sg), 6),
            "profit_factor_proxy": round(s_pf, 6),
            "avg_return": round(float(sg["return_1bar"].mean()), 8)
        })

    regime_stats = []
    for keys, rg in g.groupby(["trend_regime","volatility_regime"]):
        rw = rg[rg["outcome"] == "WIN"]
        rl = rg[rg["outcome"] == "LOSS"]
        r_pf = float(rw["return_1bar"].sum()) / abs(float(rl["return_1bar"].sum())) if len(rl) and abs(float(rl["return_1bar"].sum())) > 0 else float(rw["return_1bar"].sum())
        regime_stats.append({
            "trend_regime": keys[0],
            "volatility_regime": keys[1],
            "trades": int(len(rg)),
            "win_rate": round(len(rw)/len(rg), 6),
            "profit_factor_proxy": round(r_pf, 6),
            "avg_return": round(float(rg["return_1bar"].mean()), 8)
        })

    trigger_stats = []
    for trigger, tg in g.groupby("trigger"):
        tw = tg[tg["outcome"] == "WIN"]
        tl = tg[tg["outcome"] == "LOSS"]
        t_pf = float(tw["return_1bar"].sum()) / abs(float(tl["return_1bar"].sum())) if len(tl) and abs(float(tl["return_1bar"].sum())) > 0 else float(tw["return_1bar"].sum())
        trigger_stats.append({
            "trigger": trigger,
            "trades": int(len(tg)),
            "win_rate": round(len(tw)/len(tg), 6),
            "profit_factor_proxy": round(t_pf, 6),
            "avg_return": round(float(tg["return_1bar"].mean()), 8)
        })

    best_session = sorted(session_stats, key=lambda x: (x["profit_factor_proxy"], x["win_rate"], x["trades"]), reverse=True)[0] if session_stats else None
    best_regime = sorted(regime_stats, key=lambda x: (x["profit_factor_proxy"], x["win_rate"], x["trades"]), reverse=True)[0] if regime_stats else None
    best_trigger = sorted(trigger_stats, key=lambda x: (x["profit_factor_proxy"], x["win_rate"], x["trades"]), reverse=True)[0] if trigger_stats else None

    asset_patterns = [p for p in patterns if p.get("asset") == asset]
    asset_clusters = [c for c in clusters if c.get("asset") == asset]
    asset_survivors = [s for s in survivors if s.get("asset") == asset]
    asset_mutations = [m for m in mutations if m.get("parent_asset") == asset]

    liquidity_sweep_dependence = round(float(g["prev_low_sweep"].mean()) * 100, 4) if "prev_low_sweep" in g else 0
    trend_dependency = round(len(g[g["trend_regime"] != "RANGE"]) / total * 100, 4) if total else 0
    high_vol_dependency = round(len(g[g["volatility_regime"] == "HIGH_VOL"]) / total * 100, 4) if total else 0
    low_vol_dependency = round(len(g[g["volatility_regime"] == "LOW_VOL"]) / total * 100, 4) if total else 0
    avg_energy = round(float(g["market_physics_energy"].mean()), 6) if "market_physics_energy" in g else 0
    avg_entropy = round(float(g["market_entropy_proxy"].mean()), 6) if "market_entropy_proxy" in g else 0

    personality = {
        "asset": asset,
        "status": f"P1881_{asset}_PERSONALITY_COMPLETED" if asset == "XAUUSD" else f"P1882_{asset}_PERSONALITY_COMPLETED",
        "trades": int(total),
        "wins": int(len(wins)),
        "losses": int(len(losses)),
        "win_rate": round(wr, 6),
        "profit_factor_proxy": round(pf, 6),
        "avg_return": round(avg_ret, 8),
        "best_session": best_session,
        "best_regime": best_regime,
        "best_trigger": best_trigger,
        "traits": {
            "liquidity_sweep_dependence": liquidity_sweep_dependence,
            "trend_dependency": trend_dependency,
            "high_vol_dependency": high_vol_dependency,
            "low_vol_dependency": low_vol_dependency,
            "avg_market_energy": avg_energy,
            "avg_entropy": avg_entropy,
            "execution_sensitivity": "LOW" if asset == "XAUUSD" else "MEDIUM_HIGH"
        },
        "session_stats": sorted(session_stats, key=lambda x: x["profit_factor_proxy"], reverse=True),
        "regime_stats": sorted(regime_stats, key=lambda x: x["profit_factor_proxy"], reverse=True),
        "trigger_stats": sorted(trigger_stats, key=lambda x: x["profit_factor_proxy"], reverse=True),
        "pattern_genomes": len(asset_patterns),
        "dna_clusters": len(asset_clusters),
        "survivor_mutations": len(asset_survivors),
        "total_mutations": len(asset_mutations),
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }

    asset_profiles.append(personality)

    asset_genome_library.append({
        "asset": asset,
        "genome_id": f"{asset}_GENOME_V1",
        "personality_summary": personality["traits"],
        "preferred_session": best_session["session"] if best_session else None,
        "preferred_regime": best_regime if best_regime else None,
        "preferred_trigger": best_trigger["trigger"] if best_trigger else None,
        "known_patterns": asset_patterns[:20],
        "status": "P1885_ASSET_GENOME_REGISTERED"
    })

    memory_rows.append({
        "asset": asset,
        "memory_type": "ASSET_PERSONALITY",
        "memory_payload": {
            "best_session": best_session,
            "best_regime": best_regime,
            "best_trigger": best_trigger,
            "traits": personality["traits"]
        },
        "created_at": datetime.now(UTC).isoformat()
    })

# P1883 EURUSD personality placeholder based on no elite DNA yet
eurusd_placeholder = {
    "asset": "EURUSD",
    "status": "P1883_EURUSD_PERSONALITY_PENDING_REAL_ELITE_DNA",
    "reason": "No EURUSD elite edge passed current 10Y/WF/MC pipeline yet",
    "required_next": "Run transfer learning and 10Y certification for EURUSD candidates"
}

# P1884 Cross Asset Personality
assets = {p["asset"]: p for p in asset_profiles}
if "XAUUSD" in assets and "USDJPY" in assets:
    cross_asset_rows.append({
        "status": "P1884_CROSS_ASSET_PERSONALITY_COMPLETED",
        "assets_compared": ["XAUUSD","USDJPY"],
        "xauusd_personality": assets["XAUUSD"]["traits"],
        "usdjpy_personality": assets["USDJPY"]["traits"],
        "comparison": {
            "xauusd_core": "LIQUIDITY_SWEEP_AND_EXECUTION_RESILIENCE",
            "usdjpy_core": "STATISTICAL_REVERSION_AND_EXECUTION_SENSITIVITY",
            "shared_strength": "D1_TIMEFRAME_ROBUSTNESS",
            "risk_difference": "USDJPY weakens under extreme execution stress; XAUUSD survives it"
        }
    })

asset_personality_file = ASSETS / "p1881_to_p1883_asset_personalities.json"
cross_asset_file = ASSETS / "p1884_cross_asset_personality.json"
asset_genome_file = ASSETS / "p1885_asset_genome_library.json"
memory_file = MEMORY / "p1886_market_memory_seed_from_asset_personality.json"

asset_personality_file.write_text(json.dumps(asset_profiles + [eurusd_placeholder], indent=2, ensure_ascii=False), encoding="utf-8")
cross_asset_file.write_text(json.dumps(cross_asset_rows, indent=2, ensure_ascii=False), encoding="utf-8")
asset_genome_file.write_text(json.dumps(asset_genome_library, indent=2, ensure_ascii=False), encoding="utf-8")
memory_file.write_text(json.dumps(memory_rows, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1881_TO_P1885_ASSET_PERSONALITY_FACTORY_COMPLETED",
    "P1881_XAUUSD_PERSONALITY": "COMPLETED" if "XAUUSD" in assets else "MISSING_DNA",
    "P1882_USDJPY_PERSONALITY": "COMPLETED" if "USDJPY" in assets else "MISSING_DNA",
    "P1883_EURUSD_PERSONALITY": "PENDING_REAL_ELITE_DNA",
    "P1884_CROSS_ASSET_PERSONALITY_ROWS": len(cross_asset_rows),
    "P1885_ASSET_GENOMES": len(asset_genome_library),
    "ASSET_PROFILES": asset_profiles,
    "OUTPUTS": {
        "asset_personalities": str(asset_personality_file),
        "cross_asset_personality": str(cross_asset_file),
        "asset_genome_library": str(asset_genome_file),
        "market_memory_seed": str(memory_file)
    },
    "NEXT": "P1886_TO_P1890_MARKET_MEMORY_FACTORY",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(BASE / "p1881_to_p1885_asset_personality_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
