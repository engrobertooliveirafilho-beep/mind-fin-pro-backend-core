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
        self.session_start = self.equity
        self.killed = False

    def check(self, pnl):
        if self.killed:
            return "KILLED"
        if type(pnl) not in (int,float) or not math.isfinite(pnl):
            raise ValueError("INVALID_PNL")
        self.equity += pnl
        self.peak = max(self.peak, self.equity)
        drawdown = (self.peak - self.equity) / self.peak

        if drawdown >= self.max_drawdown or (self.session_start-self.equity)/self.session_start >= self.daily_loss_limit:
            self.killed = True
            return "KILLED"
        return "OK"


class BrokerEmulator:
    def __init__(self):
        self.market = MarketDataEngine()
        self.risk = RiskEngine()
        self.trades = []

    def execute_order(self, side, volume):
        if self.risk.killed:
            raise RuntimeError("RISK_LOCKED")
        if side not in ("BUY", "SELL") or type(volume) not in (int,float) or not math.isfinite(volume) or volume <= 0:
            raise ValueError("INVALID_ORDER")
        price = self.market.tick()

        # Synthetic round trip, unit multiplier; not instrument-calibrated.
        slippage = 0.1
        direction = 1 if side == "BUY" else -1
        exec_price = price + direction * slippage
        exit_price = self.market.tick() - direction * slippage
        pnl = direction * (exit_price - exec_price) * volume

        risk_status = self.risk.check(pnl)

        trade = {
            "side": side,
            "volume": volume,
            "market_price": price,
            "exec_price": exec_price,
            "exit_price": exit_price,
            "contract_multiplier": 1,
            "data_origin": "SYNTHETIC",
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
        "status": "RISK_KILLED" if broker.risk.killed else "SYNTHETIC_ONLY",
        "edge_claim": "NONE",
        "real_orders": "FORBIDDEN",
        "trades": broker.trades,
        "final_equity": broker.risk.equity,
        "total_trades": len(broker.trades),
        "mode": "BROKER_EMULATOR_SIMULATION_ONLY"
    }


if __name__ == "__main__":
    result = run_simulation()
    print(json.dumps(result, indent=2))
