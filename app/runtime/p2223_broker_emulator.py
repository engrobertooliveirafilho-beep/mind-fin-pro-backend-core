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
        self.initial_equity = self.equity
        self.killed = False

    def check(self, pnl):
        if self.killed:
            return "KILLED"
        if not isinstance(pnl, (int, float)) or not math.isfinite(pnl):
            raise ValueError("non-finite PnL")
        self.equity += pnl
        self.peak = max(self.peak, self.equity)
        drawdown = (self.peak - self.equity) / self.peak
        # No session calendar is supplied; this is a conservative
        # session-wide loss cap, NOT certified FTMO daily reset logic.
        session_loss = (self.initial_equity - self.equity) / self.initial_equity
        if drawdown > self.max_drawdown or session_loss > self.daily_loss_limit:
            self.killed = True
        return "KILLED" if self.killed else "OK"


class BrokerEmulator:
    def __init__(self):
        self.market = MarketDataEngine()
        self.risk = RiskEngine()
        self.trades = []

    def execute_order(self, side, volume):
        if self.risk.killed:
            raise RuntimeError("PAPER_RISK_KILL_SWITCH")
        if side not in ("BUY", "SELL"):
            raise ValueError("invalid PAPER order side")
        if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not math.isfinite(volume) or volume <= 0:
            raise ValueError("invalid PAPER order volume")
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
        "status": "KILLED" if broker.risk.killed else "SIMULATED",
        "trades": broker.trades,
        "final_equity": broker.risk.equity,
        "total_trades": len(broker.trades),
        "mode": "BROKER_EMULATOR_SIMULATION_ONLY"
    }


if __name__ == "__main__":
    result = run_simulation()
    print(json.dumps(result, indent=2))
