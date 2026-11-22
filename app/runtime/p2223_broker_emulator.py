from __future__ import annotations
import json
import math
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
        self.day_start_equity = self.equity
        self.killed = False

    def check(self, pnl):
        if self.killed:
            return "KILLED"
        if isinstance(pnl, bool) or not isinstance(pnl, (int, float)) or not math.isfinite(pnl):
            self.killed = True
            return "KILLED"
        self.equity += pnl
        if not math.isfinite(self.equity) or self.equity <= 0:
            self.killed = True
            return "KILLED"
        self.peak = max(self.peak, self.equity)
        drawdown = (self.peak - self.equity) / self.peak
        daily_loss = (self.day_start_equity - self.equity) / self.day_start_equity
        if drawdown >= self.max_drawdown or daily_loss >= self.daily_loss_limit:
            self.killed = True
            return "KILLED"
        return "OK"


class BrokerEmulator:
    def __init__(self):
        self.market = MarketDataEngine()
        self.risk = RiskEngine()
        self.trades = []
        self.killed = False

    def execute_order(self, side, volume):
        if self.killed or self.risk.killed:
            self.killed = True
            raise RuntimeError("P2223_RISK_KILL_LATCHED")
        if side not in ("BUY", "SELL"):
            raise ValueError("P2223_INVALID_SIDE")
        if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not math.isfinite(volume) or volume <= 0:
            raise ValueError("P2223_INVALID_VOLUME")
        price = self.market.tick()

        # Slippage simulation
        slippage = random.uniform(-0.1, 0.1)
        if (
            not isinstance(price, (int, float))
            or isinstance(price, bool)
            or not math.isfinite(price)
            or price <= 0
            or not isinstance(slippage, (int, float))
            or isinstance(slippage, bool)
            or not math.isfinite(slippage)
        ):
            self.killed = True
            self.risk.killed = True
            raise RuntimeError("P2223_INVALID_MARKET_EXECUTION")
        exec_price = price + slippage
        if not math.isfinite(exec_price) or exec_price <= 0:
            self.killed = True
            self.risk.killed = True
            raise RuntimeError("P2223_INVALID_MARKET_EXECUTION")

        pnl = 0
        if side == "BUY":
            pnl = random.uniform(-50, 120)
        else:
            pnl = random.uniform(-60, 140)

        risk_status = self.risk.check(pnl)

        if risk_status == "KILLED":
            self.killed = True

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
    if type(cycles) is not int or cycles < 1:
        raise ValueError("P2223_INVALID_CYCLES")
    broker = BrokerEmulator()

    for i in range(cycles):
        side = random.choice(["BUY", "SELL"])
        volume = random.randint(1, 10)

        trade = broker.execute_order(side, volume)

        if trade["risk"] == "KILLED":
            break

    return {
        "status": "SIMULATION_ONLY_NOT_CERTIFIED",
        "trades": broker.trades,
        "final_equity": broker.risk.equity,
        "total_trades": len(broker.trades),
        "mode": "BROKER_EMULATOR_SIMULATION_ONLY"
    }


if __name__ == "__main__":
    result = run_simulation()
    print(json.dumps(result, indent=2))
