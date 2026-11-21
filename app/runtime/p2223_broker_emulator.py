from __future__ import annotations
import json
import random
import math
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
        self.halted = False
        self.session_start_equity = self.equity

    def check(self, pnl):
        if self.halted:
            raise RuntimeError("simulated risk engine halted")
        if type(pnl) not in (int, float) or not math.isfinite(pnl):
            raise ValueError("invalid simulated pnl")
        if (self.session_start_equity <= 0 or self.peak <= 0
                or not all(math.isfinite(v) for v in (self.equity, self.peak, self.session_start_equity))):
            self.halted = True
            raise RuntimeError("invalid simulated risk baseline")
        if (self.equity <= 0
                or (self.peak - self.equity) / self.peak > self.max_drawdown
                or (self.session_start_equity - self.equity) / self.session_start_equity > self.daily_loss_limit):
            self.halted = True
            raise RuntimeError("simulated risk engine halted")
        self.equity += pnl
        self.peak = max(self.peak, self.equity)
        drawdown = (self.peak - self.equity) / self.peak

        session_loss = (self.session_start_equity - self.equity) / self.session_start_equity
        if drawdown > self.max_drawdown or session_loss > self.daily_loss_limit:
            self.halted = True
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
        if self.risk.halted or self.risk.equity <= 0 or self.risk.peak <= 0 or self.risk.session_start_equity <= 0 or (self.risk.peak - self.risk.equity) / self.risk.peak > self.risk.max_drawdown or (self.risk.session_start_equity - self.risk.equity) / self.risk.session_start_equity > self.risk.daily_loss_limit:
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
    if type(cycles) is not int:
        raise TypeError("cycles must be an integer")
    if not 1 <= cycles <= 10000:
        raise ValueError("cycles out of bounds")
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
