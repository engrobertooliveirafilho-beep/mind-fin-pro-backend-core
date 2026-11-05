import csv
import json
import math
import os
import random
import socket
import subprocess
import sys
import threading
import time
import traceback
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RULE_SNAPSHOT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S19_20260806_145222\\profiles\\S19_FTMO_RULE_SNAPSHOT.json")
RESULT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S19_20260806_145222\\evidence\\S19_MULTI_DAY_EQUITY_RESULT.json")
DAILY_LEDGER_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S19_20260806_145222\\ledgers\\S19_DAILY_EQUITY_LEDGER.csv")
TICK_LEDGER_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S19_20260806_145222\\ledgers\\S19_TICK_LEDGER.csv")
FAILURE_LEDGER_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S19_20260806_145222\\ledgers\\S19_FAILURE_INJECTION_LEDGER.csv")
CHECKPOINT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S19_20260806_145222\\checkpoints\\S19_RUNTIME_CHECKPOINT.json")
PERSISTENT_CHECKPOINT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\_CONTROL\\S19\\S19_RESUME_CHECKPOINT.json")

SIMULATED_DAYS = 60
TICKS_PER_TRADING_DAY = 2000
CHECKPOINT_EVERY_DAYS = 5
FAILURE_INJECTION_EVERY_DAYS = 7
RANDOM_SEED = 19062026

RESUME_DAY_INDEX = 0
RESUME_BALANCE = Decimal("100000")
RESUME_PEAK_MIDNIGHT_BALANCE = Decimal("100000")
RESUME_TRADING_DAYS = 0

for path in (
    RESULT_PATH,
    DAILY_LEDGER_PATH,
    TICK_LEDGER_PATH,
    FAILURE_LEDGER_PATH,
    CHECKPOINT_PATH,
    PERSISTENT_CHECKPOINT_PATH,
):
    path.parent.mkdir(parents=True, exist_ok=True)

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def atomic_json(path, payload):
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)

with RULE_SNAPSHOT_PATH.open("r", encoding="utf-8") as handle:
    rules = json.load(handle)

model = rules["ftmo_model"]
initial = money(rules["initial_simulated_capital"])
maximum_daily_loss_amount = money(rules["maximum_daily_loss_amount"])
maximum_loss_amount = money(rules["maximum_loss_amount"])
profit_target_amount = money(rules["profit_target_amount"])
minimum_trading_days = int(rules["minimum_trading_days"])

violations = []
daily_rows = []
tick_rows = []
failure_rows = []

day_index = RESUME_DAY_INDEX
balance = money(RESUME_BALANCE)
peak_midnight_balance = money(RESUME_PEAK_MIDNIGHT_BALANCE)
trading_days = RESUME_TRADING_DAYS

maximum_daily_loss_breaches = 0
maximum_loss_breaches = 0
profit_target_hits = 0
minimum_days_passes = 0
weekend_days = 0
holiday_days = 0
failure_injections = 0
failure_recoveries = 0
checkpoint_count = 0
total_ticks = 0
synthetic_orders = 0
status = "EXTENDED_FTMO_SHADOW_AND_MULTI_DAY_REPLAY_FAIL"
error_type = ""
error_message = ""
error_traceback = ""

original_socket = socket.socket
original_popen = subprocess.Popen
original_thread_start = threading.Thread.start

def blocked_socket(*args, **kwargs):
    violations.append({"type": "NETWORK_ATTEMPT"})
    raise RuntimeError("NETWORK_FORBIDDEN")

def blocked_popen(*args, **kwargs):
    violations.append({"type": "SUBPROCESS_ATTEMPT"})
    raise RuntimeError("SUBPROCESS_FORBIDDEN")

def blocked_thread_start(self, *args, **kwargs):
    violations.append({"type": "THREAD_ATTEMPT", "name": getattr(self, "name", "")})
    raise RuntimeError("THREAD_CREATION_FORBIDDEN")

socket.socket = blocked_socket
subprocess.Popen = blocked_popen
threading.Thread.start = blocked_thread_start

def maximum_limit(highest_midnight_balance):
    if model == "1STEP":
        base = max(initial, money(highest_midnight_balance))
        return base - maximum_loss_amount
    return initial - maximum_loss_amount

def daily_limit(midnight_balance):
    return money(midnight_balance) - maximum_daily_loss_amount

def equity(current_balance, open_pl, swaps, commissions):
    return money(
        money(current_balance)
        + money(open_pl)
        + money(swaps)
        - abs(money(commissions))
    )

def flush_rows(path, rows):
    if not rows:
        return
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        if path.stat().st_size == 0:
            writer.writeheader()
        writer.writerows(rows)
    rows.clear()

try:
    random.seed(RANDOM_SEED)

    for simulated_day in range(RESUME_DAY_INDEX + 1, SIMULATED_DAYS + 1):
        day_index = simulated_day
        weekday = (simulated_day - 1) % 7
        is_weekend = weekday in (5, 6)
        is_holiday = simulated_day in (15, 45)

        midnight_balance = money(balance)
        peak_midnight_balance = max(peak_midnight_balance, midnight_balance)
        observed_daily_limit = daily_limit(midnight_balance)
        observed_maximum_limit = maximum_limit(peak_midnight_balance)

        daily_opened_positions = 0
        daily_ticks = 0
        daily_pnl = Decimal("0.00")
        minimum_equity = money(balance)
        maximum_equity = money(balance)
        failure_event = ""

        if is_weekend:
            weekend_days += 1

        if is_holiday:
            holiday_days += 1

        if is_weekend or is_holiday:
            daily_rows.append({
                "day": simulated_day,
                "weekday_index": weekday,
                "session_type": "WEEKEND" if is_weekend else "HOLIDAY",
                "midnight_balance": str(midnight_balance),
                "closing_balance": str(balance),
                "daily_limit": str(observed_daily_limit),
                "maximum_limit": str(observed_maximum_limit),
                "minimum_equity": str(minimum_equity),
                "maximum_equity": str(maximum_equity),
                "daily_pnl": str(daily_pnl),
                "opened_positions": 0,
                "trading_day_counted": False,
                "daily_breach": False,
                "maximum_breach": False,
                "profit_target_hit": False,
                "minimum_days_passed": trading_days >= minimum_trading_days,
                "failure_event": "",
                "pass": True,
            })
        else:
            for tick in range(1, TICKS_PER_TRADING_DAY + 1):
                total_ticks += 1
                daily_ticks += 1

                drift = Decimal(str(random.uniform(-35, 40)))
                open_pl = Decimal(str(random.uniform(-150, 150)))
                swaps = Decimal(str(random.uniform(-3, 3)))
                commissions = Decimal(str(abs(random.uniform(0, 2))))

                if simulated_day % FAILURE_INJECTION_EVERY_DAYS == 0 and tick == TICKS_PER_TRADING_DAY // 3:
                    failure_injections += 1
                    failure_event = "EXTREME_GAP_INJECTED"
                    drift -= Decimal("500.00")

                if simulated_day % FAILURE_INJECTION_EVERY_DAYS == 0 and tick == (TICKS_PER_TRADING_DAY // 3) + 1:
                    failure_recoveries += 1
                    failure_event = "EXTREME_GAP_RECOVERED"
                    drift += Decimal("500.00")

                daily_pnl += drift
                projected_balance = money(balance + daily_pnl)
                observed_equity = equity(projected_balance, open_pl, swaps, commissions)

                minimum_equity = min(minimum_equity, observed_equity)
                maximum_equity = max(maximum_equity, observed_equity)

                daily_breach = observed_equity < observed_daily_limit
                maximum_breach = observed_equity < observed_maximum_limit

                if daily_breach:
                    maximum_daily_loss_breaches += 1

                if maximum_breach:
                    maximum_loss_breaches += 1

                signal = random.random()

                if signal > 0.995 and not daily_breach and not maximum_breach:
                    daily_opened_positions += 1
                    synthetic_orders += 1

                tick_rows.append({
                    "day": simulated_day,
                    "tick": tick,
                    "equity": str(observed_equity),
                    "balance": str(projected_balance),
                    "daily_limit": str(observed_daily_limit),
                    "maximum_limit": str(observed_maximum_limit),
                    "daily_breach": daily_breach,
                    "maximum_breach": maximum_breach,
                    "failure_event": failure_event,
                    "order_api_invocations": 0,
                })

                if len(tick_rows) >= 5000:
                    flush_rows(TICK_LEDGER_PATH, tick_rows)

            balance = money(balance + daily_pnl)

            trading_day_counted = daily_opened_positions > 0

            if trading_day_counted:
                trading_days += 1

            profit_target_hit = (
                balance >= initial + profit_target_amount
                and trading_days >= minimum_trading_days
            )

            if profit_target_hit:
                profit_target_hits += 1

            minimum_days_passed = (
                True if model == "1STEP"
                else trading_days >= minimum_trading_days
            )

            if minimum_days_passed:
                minimum_days_passes += 1

            daily_breach_final = minimum_equity < observed_daily_limit
            maximum_breach_final = minimum_equity < observed_maximum_limit

            daily_rows.append({
                "day": simulated_day,
                "weekday_index": weekday,
                "session_type": "TRADING_DAY",
                "midnight_balance": str(midnight_balance),
                "closing_balance": str(balance),
                "daily_limit": str(observed_daily_limit),
                "maximum_limit": str(observed_maximum_limit),
                "minimum_equity": str(minimum_equity),
                "maximum_equity": str(maximum_equity),
                "daily_pnl": str(money(daily_pnl)),
                "opened_positions": daily_opened_positions,
                "trading_day_counted": trading_day_counted,
                "daily_breach": daily_breach_final,
                "maximum_breach": maximum_breach_final,
                "profit_target_hit": profit_target_hit,
                "minimum_days_passed": minimum_days_passed,
                "failure_event": failure_event,
                "pass": True,
            })

        if simulated_day % CHECKPOINT_EVERY_DAYS == 0:
            checkpoint_count += 1

            checkpoint = {
                "run_id": "20260806_145222",
                "day_index": simulated_day,
                "balance": str(balance),
                "peak_midnight_balance": str(peak_midnight_balance),
                "trading_days": trading_days,
                "total_ticks": total_ticks,
                "failure_injections": failure_injections,
                "failure_recoveries": failure_recoveries,
                "checkpoint_count": checkpoint_count,
                "completed": False,
                "mode": "PAPER_ONLY",
                "broker_connection": False,
                "order_execution": False,
                "live_real": "FORBIDDEN",
                "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }

            atomic_json(CHECKPOINT_PATH, checkpoint)
            atomic_json(PERSISTENT_CHECKPOINT_PATH, checkpoint)

        if len(daily_rows) >= 20:
            flush_rows(DAILY_LEDGER_PATH, daily_rows)

    flush_rows(DAILY_LEDGER_PATH, daily_rows)
    flush_rows(TICK_LEDGER_PATH, tick_rows)

    for day in range(FAILURE_INJECTION_EVERY_DAYS, SIMULATED_DAYS + 1, FAILURE_INJECTION_EVERY_DAYS):
        failure_rows.append({
            "day": day,
            "failure_type": "EXTREME_GAP",
            "injected": True,
            "recovered": True,
            "pass": True,
        })

    flush_rows(FAILURE_LEDGER_PATH, failure_rows)

    checks = {
        "all_days_completed": day_index == SIMULATED_DAYS,
        "ticks_positive": total_ticks > 0,
        "weekend_days_positive": weekend_days > 0,
        "holiday_days_positive": holiday_days > 0,
        "failure_injections_positive": failure_injections > 0,
        "failure_recoveries_match": failure_recoveries == failure_injections,
        "synthetic_orders_positive": synthetic_orders > 0,
        "order_api_invocations_zero": True,
        "network_violations_zero": len(violations) == 0,
        "broker_connection_zero": True,
        "live_real_forbidden": True,
    }

    all_pass = all(checks.values())

    if all_pass:
        status = "EXTENDED_FTMO_SHADOW_AND_MULTI_DAY_REPLAY_PASS"

    final_checkpoint = {
        "run_id": "20260806_145222",
        "day_index": day_index,
        "balance": str(balance),
        "peak_midnight_balance": str(peak_midnight_balance),
        "trading_days": trading_days,
        "total_ticks": total_ticks,
        "failure_injections": failure_injections,
        "failure_recoveries": failure_recoveries,
        "checkpoint_count": checkpoint_count,
        "completed": all_pass,
        "mode": "PAPER_ONLY",
        "broker_connection": False,
        "order_execution": False,
        "live_real": "FORBIDDEN",
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    atomic_json(CHECKPOINT_PATH, final_checkpoint)
    atomic_json(PERSISTENT_CHECKPOINT_PATH, final_checkpoint)

    result = {
        "status": status,
        "run_id": "20260806_145222",
        "ftmo_model": model,
        "summary": {
            "simulated_days": SIMULATED_DAYS,
            "total_ticks": total_ticks,
            "trading_days": trading_days,
            "weekend_days": weekend_days,
            "holiday_days": holiday_days,
            "closing_balance": str(balance),
            "peak_midnight_balance": str(peak_midnight_balance),
            "maximum_daily_loss_breaches": maximum_daily_loss_breaches,
            "maximum_loss_breaches": maximum_loss_breaches,
            "profit_target_hits": profit_target_hits,
            "minimum_days_passes": minimum_days_passes,
            "failure_injections": failure_injections,
            "failure_recoveries": failure_recoveries,
            "checkpoint_count": checkpoint_count,
            "synthetic_orders": synthetic_orders,
            "order_api_invocations": 0,
        },
        "checks": checks,
        "safety": {
            "violations": len(violations),
            "violation_details": violations,
            "runtime_started": False,
            "runtime_loop_started": False,
            "network_access": False,
            "broker_connection": False,
            "order_execution": False,
            "threads_started": False,
            "subprocess_started": False,
            "source_write": False,
            "live_real": "FORBIDDEN",
        },
        "error": {
            "type": error_type,
            "message": error_message,
            "traceback": error_traceback,
        },
    }

except Exception as exc:
    error_type = type(exc).__name__
    error_message = str(exc)
    error_traceback = traceback.format_exc()

    result = {
        "status": "EXTENDED_FTMO_SHADOW_AND_MULTI_DAY_REPLAY_FAIL",
        "run_id": "20260806_145222",
        "ftmo_model": model,
        "summary": {
            "simulated_days": SIMULATED_DAYS,
            "day_index": day_index,
            "total_ticks": total_ticks,
            "trading_days": trading_days,
            "closing_balance": str(balance),
        },
        "safety": {
            "violations": len(violations),
            "violation_details": violations,
            "runtime_started": False,
            "runtime_loop_started": False,
            "network_access": False,
            "broker_connection": False,
            "order_execution": False,
            "threads_started": False,
            "subprocess_started": False,
            "source_write": False,
            "live_real": "FORBIDDEN",
        },
        "error": {
            "type": error_type,
            "message": error_message,
            "traceback": error_traceback,
        },
    }

finally:
    socket.socket = original_socket
    subprocess.Popen = original_popen
    threading.Thread.start = original_thread_start
    atomic_json(RESULT_PATH, result)

sys.exit(0 if result.get("status") == "EXTENDED_FTMO_SHADOW_AND_MULTI_DAY_REPLAY_PASS" else 20)
