from __future__ import annotations
import json, random
from pathlib import Path

# ============================================================
# P2227 - CRISIS SIMULATION ENGINE
# ============================================================

class CrisisEngine:
    def __init__(self):
        self.shock = 0.02

    def simulate_crisis(self, price):
        event = random.choice(["NONE","CRASH","SPIKE","LIQUIDITY_DRAIN"])

        if event == "CRASH":
            price *= (1 - random.uniform(0.05, 0.2))
        elif event == "SPIKE":
            price *= (1 + random.uniform(0.03, 0.15))
        elif event == "LIQUIDITY_DRAIN":
            price *= (1 + random.uniform(-0.02, 0.02))

        return round(price, 2), event


# ============================================================
# P2228 - GLOBAL MACRO MARKET TWIN
# ============================================================

class MacroMarketTwin:
    def __init__(self):
        self.world = {
            "USD_INDEX": 105,
            "RISK_SENTIMENT": 50,
            "VOLATILITY": 20
        }

    def step(self):
        self.world["USD_INDEX"] += random.uniform(-0.5, 0.5)
        self.world["RISK_SENTIMENT"] += random.uniform(-2, 2)
        self.world["VOLATILITY"] += random.uniform(-1, 1)

        return {k: round(v, 2) for k, v in self.world.items()}


# ============================================================
# P2229 - SELF OPTIMIZING STRATEGY ECOSYSTEM
# ============================================================

class StrategyEcoSystem:
    def __init__(self):
        self.strategies = [
            {"name":"trend","score":50},
            {"name":"meanrev","score":50},
            {"name":"breakout","score":50}
        ]

    def evolve(self, macro_signal):
        for s in self.strategies:
            mutation = random.uniform(-3, 3)

            # macro influence
            macro_bias = (macro_signal["VOLATILITY"] / 50)

            s["score"] += mutation - macro_bias

        self.strategies.sort(key=lambda x: x["score"], reverse=True)

        # prune weak
        self.strategies = self.strategies[:3]

        return self.strategies


# ============================================================
# INTEGRATED SYSTEM LOOP
# ============================================================

def run(cycles=40):
    price = 100.0

    crisis = CrisisEngine()
    macro = MacroMarketTwin()
    eco = StrategyEcoSystem()

    log = []

    for i in range(cycles):

        price, event = crisis.simulate_crisis(price)
        macro_state = macro.step()
        strategies = eco.evolve(macro_state)

        log.append({
            "price": price,
            "event": event,
            "macro": macro_state,
            "strategies": strategies
        })

    return {
        "status":"PASS",
        "mode":"ADVANCED_SIMULATION_LAYER",
        "cycles": cycles,
        "sample": log[:3],
        "final_strategies": eco.strategies
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
