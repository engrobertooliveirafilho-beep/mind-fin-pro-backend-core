from __future__ import annotations
import json
import random
import time
from pathlib import Path

# =========================
# BROKER EMULATOR CORE
# =========================

class MarketDataEngine:
    def __init__(self):
        self.price = 100.0
        self.volatility = 0.02

    def tick(self):
        move = random.uniform(-1, 1) * self.volatility * self.price
        self.price += move
        return round(self.price, 2)


class RiskEngine:
    def __init__(self):
        self.max_drawdown = 0.05
        self.daily_loss_limit = 0.03
        self.equity = 100000
        self.peak = self.equity

    def check(self, pnl):
        self.equity += pnl
        self.peak = max(self.peak, self.equity)
        drawdown = (self.peak - self.equity) / self.peak

        if drawdown > self.max_drawdown:
            return "KILLED"
        return "OK"


class BrokerEmulator:
    def __init__(self):
        self.market = MarketDataEngine()
        self.risk = RiskEngine()
        self.trades = []

    def execute_order(self, side, volume):
        # Simulation-only: reject malformed intentions before changing any state.
        if side not in ("BUY", "SELL"):
            raise ValueError("unsupported simulated order side")
        if type(volume) is not int or volume <= 0:
            raise ValueError("simulated order volume must be a positive integer")
        if self.risk.equity <= 0 or (self.risk.peak - self.risk.equity) / self.risk.peak > self.risk.max_drawdown:
            raise RuntimeError("simulated risk engine halted")
        price = self.market.tick()

        # Slippage simulation
        slippage = random.uniform(-0.1, 0.1)
        exec_price = price + slippage

        pnl = 0
        if side == "BUY":
            pnl = random.uniform(-50, 120)
        else:
            pnl = random.uniform(-60, 140)

        risk_status = self.risk.check(pnl)

        trade = {
            "side": side,
            "volume": volume,
            "market_price": price,
            "exec_price": exec_price,
            "slippage": slippage,
            "pnl": pnl,
            "risk": risk_status,
            "equity": self.risk.equity
        }

        self.trades.append(trade)
        return trade


def run_simulation(cycles=50):
    broker = BrokerEmulator()

    for i in range(cycles):
        side = random.choice(["BUY", "SELL"])
        volume = random.randint(1, 10)

        trade = broker.execute_order(side, volume)

        if trade["risk"] == "KILLED":
            break

    return {
        "status": "PASS",
        "trades": broker.trades,
        "final_equity": broker.risk.equity,
        "total_trades": len(broker.trades),
        "mode": "BROKER_EMULATOR_SIMULATION_ONLY"
    }


if __name__ == "__main__":
    result = run_simulation()
    print(json.dumps(result, indent=2))
