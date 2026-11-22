from __future__ import annotations
import json, random, math
from pathlib import Path

# ============================================================
# P2227 - CRISIS SIMULATION ENGINE
# ============================================================

class CrisisEngine:
    def __init__(self):
        self.shock = 0.02

    def simulate_crisis(self, price):
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
            raise ValueError("P2227_INVALID_PRICE")
        event = random.choice(["NONE","CRASH","SPIKE","LIQUIDITY_DRAIN"])
        if event not in ("NONE", "CRASH", "SPIKE", "LIQUIDITY_DRAIN"):
            raise RuntimeError("P2227_INVALID_CRISIS_EVENT")

        if event == "CRASH":
            price *= (1 - random.uniform(0.05, 0.2))
        elif event == "SPIKE":
            price *= (1 + random.uniform(0.03, 0.15))
        elif event == "LIQUIDITY_DRAIN":
            price *= (1 + random.uniform(-0.02, 0.02))

        if not math.isfinite(price) or price < 0.005:
            raise RuntimeError("P2227_INVALID_CRISIS_PRICE")
        rounded_price = round(price, 2)
        if rounded_price <= 0:
            raise RuntimeError("P2227_INVALID_CRISIS_PRICE")
        return rounded_price, event


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
        updated = {}
        for name, bounds in (("USD_INDEX", (-0.5, 0.5)), ("RISK_SENTIMENT", (-2, 2)), ("VOLATILITY", (-1, 1))):
            move = random.uniform(*bounds)
            if isinstance(move, bool) or not isinstance(move, (int, float)) or not math.isfinite(move) or not bounds[0] <= move <= bounds[1]:
                raise RuntimeError("P2228_INVALID_MACRO_SHOCK")
            value = self.world[name] + move
            if not math.isfinite(value):
                raise RuntimeError("P2228_INVALID_MACRO_STATE")
            updated[name] = value
        self.world = updated
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
        if not isinstance(macro_signal, dict) or isinstance(macro_signal.get("VOLATILITY"), bool) or not isinstance(macro_signal.get("VOLATILITY"), (int, float)) or not math.isfinite(macro_signal["VOLATILITY"]):
            raise ValueError("P2229_INVALID_MACRO_SIGNAL")
        updated = []
        for s in self.strategies:
            mutation = random.uniform(-3, 3)
            if isinstance(mutation, bool) or not isinstance(mutation, (int, float)) or not math.isfinite(mutation) or not -3 <= mutation <= 3:
                raise RuntimeError("P2229_INVALID_MUTATION")

            # macro influence
            macro_bias = (macro_signal["VOLATILITY"] / 50)

            score = s["score"] + mutation - macro_bias
            if not math.isfinite(score):
                raise RuntimeError("P2229_INVALID_SCORE")
            updated.append({**s, "score": score})

        updated.sort(key=lambda x: x["score"], reverse=True)
        self.strategies = updated[:3]
        return [dict(s) for s in self.strategies]


# ============================================================
# INTEGRATED SYSTEM LOOP
# ============================================================

def run(cycles=40):
    if type(cycles) is not int or not 1 <= cycles <= 10000:
        raise ValueError("P2227_INVALID_CYCLES")
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
        "status":"SIMULATION_ONLY_NOT_CERTIFIED",
        "mode":"ADVANCED_SIMULATION_LAYER",
        "cycles": cycles,
        "sample": log[:3],
        "final_strategies": eco.strategies
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
