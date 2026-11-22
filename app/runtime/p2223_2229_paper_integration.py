"""P2223-P2229: isolated PAPER-only integration of recovered original engines.

No broker orders are generated. The broker's risk engine is observed, not bypassed.
"""
from __future__ import annotations

import math
from app.runtime.p2223_broker_emulator import BrokerEmulator
from app.runtime.p2224_2226_institutional_core import OrderBookSimulator, MarketDigitalTwin, StrategyEvolutionEngine
from app.runtime.p2227_2229_advanced_layer import CrisisEngine, MacroMarketTwin, StrategyEcoSystem


def run_paper_pipeline(cycles=3, *, broker=None):
    if type(cycles) is not int or not 1 <= cycles <= 1000:
        raise ValueError("P2223_P2229_INVALID_CYCLES")
    broker = BrokerEmulator() if broker is None else broker
    if not isinstance(broker, BrokerEmulator):
        raise TypeError("P2223_P2229_INVALID_BROKER")
    if broker.killed or broker.risk.killed:
        raise RuntimeError("P2223_P2229_RISK_KILLED")
    if broker.trades:
        raise RuntimeError("P2223_P2229_DIRTY_BROKER")
    initial_risk = (broker.risk.equity, broker.risk.peak, broker.risk.day_start_equity)
    book = OrderBookSimulator()
    market = MarketDigitalTwin()
    strategy = StrategyEvolutionEngine()
    crisis = CrisisEngine()
    macro = MacroMarketTwin()
    ecosystem = StrategyEcoSystem()
    price = 100.0
    samples = []
    for cycle in range(cycles):
        if broker.killed or broker.risk.killed:
            raise RuntimeError("P2223_P2229_RISK_KILLED")
        quote = book.update_book()
        assets = market.step()
        strategies = strategy.evolve()
        price, event = crisis.simulate_crisis(price)
        macro_state = macro.step()
        ecosystem_state = ecosystem.evolve(macro_state)
        if not math.isfinite(price) or price <= 0 or not all(math.isfinite(x) and x > 0 for x in assets.values()):
            raise RuntimeError("P2223_P2229_INVALID_SIMULATION_STATE")
        if broker.killed or broker.risk.killed:
            raise RuntimeError("P2223_P2229_RISK_KILLED")
        if broker.trades or initial_risk != (broker.risk.equity, broker.risk.peak, broker.risk.day_start_equity):
            raise RuntimeError("P2223_P2229_BROKER_MUTATED")
        if cycle < 3:
            samples.append({
                "book": quote,
                "market": assets,
                "strategies": strategies,
                "crisis": {"price": price, "event": event},
                "macro": macro_state,
                "ecosystem": ecosystem_state,
            })
    return {
        "status": "SIMULATION_ONLY_NOT_CERTIFIED",
        "mode": "PAPER_ONLY",
        "cycles": cycles,
        "broker_orders_created": 0,
        "broker_trades_observed": len(broker.trades),
        "broker_risk": "OK",
        "sample": samples,
    }
