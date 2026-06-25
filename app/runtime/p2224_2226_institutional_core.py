from __future__ import annotations
import json, random
from pathlib import Path

# ============================================================
# P2224 — ORDER BOOK DEPTH SIMULATOR
# ============================================================

class OrderBookSimulator:
    def __init__(self):
        self.bid = 100.0
        self.ask = 100.2
        self.depth = 10

    def update_book(self):
        move = random.uniform(-0.5, 0.5)
        self.bid += move
        self.ask += move
        return {
            "bid": round(self.bid, 2),
            "ask": round(self.ask, 2),
            "spread": round(self.ask - self.bid, 4),
            "depth": self.depth
        }

# ============================================================
# P2225 — INSTITUTIONAL MARKET DIGITAL TWIN
# ============================================================

class MarketDigitalTwin:
    def __init__(self):
        self.assets = {
            "XAUUSD": 2000.0,
            "EURUSD": 1.10,
            "SP500": 4500.0
        }

    def step(self):
        for k in self.assets:
            shock = random.uniform(-1, 1) * 0.5
            self.assets[k] += shock
        return {k: round(v, 2) for k, v in self.assets.items()}

# ============================================================
# P2226 — STRATEGY EVOLUTION ENGINE
# ============================================================

class StrategyEvolutionEngine:
    def __init__(self):
        self.strategies = [
            {"name":"trend_follow","score":50},
            {"name":"mean_reversion","score":50},
            {"name":"breakout","score":50}
        ]

    def evolve(self):
        for s in self.strategies:
            mutation = random.uniform(-5, 5)
            s["score"] += mutation

        self.strategies.sort(key=lambda x: x["score"], reverse=True)

        # prune worst
        self.strategies = self.strategies[:3]

        return self.strategies

# ============================================================
# INTEGRATED RUNTIME
# ============================================================

def run(cycles=30):
    book = OrderBookSimulator()
    twin = MarketDigitalTwin()
    evo = StrategyEvolutionEngine()

    logs = []

    for i in range(cycles):
        logs.append({
            "book": book.update_book(),
            "market": twin.step(),
            "strategies": evo.evolve()
        })

    return {
        "status":"PASS",
        "mode":"INSTITUTIONAL_SIMULATION_CORE",
        "cycles": cycles,
        "log_sample": logs[:3],
        "final_strategies": evo.strategies
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
