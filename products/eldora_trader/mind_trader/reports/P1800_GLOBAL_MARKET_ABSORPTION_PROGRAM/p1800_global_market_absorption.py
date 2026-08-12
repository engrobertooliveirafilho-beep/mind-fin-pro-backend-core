import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1800_GLOBAL_MARKET_ABSORPTION_PROGRAM")

asset_universe = {
    "FOREX_MAJOR": [
        "EURUSD","GBPUSD","USDJPY","AUDUSD","NZDUSD","USDCAD","USDCHF"
    ],
    "FOREX_CROSS": [
        "EURJPY","GBPJPY","EURGBP","AUDJPY","CADJPY","CHFJPY","EURAUD","GBPAUD"
    ],
    "METALS": [
        "XAUUSD","XAGUSD","XPTUSD","XPDUSD"
    ],
    "INDICES": [
        "US30","NAS100","SPX500","GER40","UK100","JPN225"
    ],
    "CRYPTO": [
        "BTCUSD","ETHUSD","SOLUSD","BNBUSD","XRPUSD"
    ],
    "COMMODITIES": [
        "WTI","BRENT","NATGAS","COPPER"
    ],
    "BRAZIL_CORE": [
        "WINFUT","WDOFUT","IBOV","PETR4","VALE3","ITUB4","BBDC4","BBAS3"
    ]
}

timeframes = ["M1","M5","M15","M30","H1","H4","D1"]

strategies = [
    "EMA_CROSS",
    "SMA_CROSS",
    "RSI_REVERSION",
    "BOLLINGER_REVERSION",
    "DONCHIAN_BREAKOUT",
    "ATR_TREND",
    "VWAP_REVERSION",
    "MACD_TREND",
    "FIBO_RETRACE",
    "LIQUIDITY_SWEEP_TRIGGER"
]

jobs = []

for market, assets in asset_universe.items():
    for asset in assets:
        for tf in timeframes:
            for strat in strategies:
                jobs.append({
                    "market": market,
                    "asset": asset,
                    "timeframe": tf,
                    "strategy_family": strat,
                    "history_targets": {
                        "research_months": 6,
                        "candidate_years": 2,
                        "institutional_years": 5,
                        "elite_years": 10
                    },
                    "priority": "HIGH" if asset in ["XAUUSD","USDJPY","GBPUSD","EURUSD","USDCAD","BTCUSD","NAS100"] else "NORMAL",
                    "mode": "RESEARCH_ONLY",
                    "REAL_ORDERS": "FORBIDDEN",
                    "FTMO_REAL": "FORBIDDEN",
                    "MT5_REAL": "FORBIDDEN"
                })

black_swan_library = [
    "COVID_2020",
    "RATE_HIKE_CYCLE_2022",
    "BANKING_STRESS_2023",
    "WAR_RISK_REGIME",
    "FLASH_CRASH",
    "INFLATION_SHOCK",
    "FOMC_HIGH_VOLATILITY",
    "NFP_HIGH_VOLATILITY",
    "CPI_HIGH_VOLATILITY"
]

market_personality_template = []
for market, assets in asset_universe.items():
    for asset in assets:
        market_personality_template.append({
            "asset": asset,
            "market": market,
            "personality_status": "PENDING_LEARNING",
            "traits_to_learn": [
                "trendiness",
                "mean_reversion_bias",
                "volatility_profile",
                "news_sensitivity",
                "session_preference",
                "tail_payoff_potential",
                "liquidity_behavior"
            ]
        })

report = {
    "STATUS": "P1800_GLOBAL_MARKET_ABSORPTION_PROGRAM_CREATED",
    "MARKET_GROUPS": len(asset_universe),
    "ASSETS_TOTAL": sum(len(v) for v in asset_universe.values()),
    "TIMEFRAMES": timeframes,
    "STRATEGY_FAMILIES": len(strategies),
    "GLOBAL_RESEARCH_JOBS": len(jobs),
    "BLACK_SWAN_EVENTS": black_swan_library,
    "NEXT": "P1801_BUILD_GLOBAL_HARVEST_QUEUE_AND_10Y_DATA_PROGRAM",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT/"global_asset_universe.json").write_text(json.dumps(asset_universe, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT/"global_research_jobs.json").write_text(json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT/"black_swan_library.json").write_text(json.dumps(black_swan_library, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT/"market_personality_template.json").write_text(json.dumps(market_personality_template, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT/"p1800_global_market_absorption_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
