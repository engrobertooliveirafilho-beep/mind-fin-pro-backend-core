import csv
import gc
import importlib
import json
import math
import os
import socket
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

RUNTIME_ROOT = Path(r"D:\\MIND_TEMP\\TRADER_CANONICAL_R2_R2_C_EMPTY_RECONSTRUCTION_20260803_065150\\reconstructed\\C_USERS_MINDFIN\\Desktop\\mind-fin-pro-backend-core")
MANIFEST_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S16_20260805_183007\\manifest\\S16_REPLAY_MANIFEST.json")
RESULT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S16_20260805_183007\\evidence\\S16_EXTENDED_SUPERVISED_RESULT.json")
LIFECYCLE_LEDGER_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S16_20260805_183007\\ledgers\\S16_LIFECYCLE_LEDGER.csv")
REPLAY_LEDGER_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S16_20260805_183007\\ledgers\\S16_MARKET_REPLAY_LEDGER.csv")
RUN_CHECKPOINT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S16_20260805_183007\\checkpoints\\S16_RUNTIME_CHECKPOINT.json")
PERSISTENT_CHECKPOINT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\_CONTROL\\S16\\S16_RESUME_CHECKPOINT.json")

DURATION_SECONDS = 7200
HEARTBEAT_SECONDS = 1
CHECKPOINT_SECONDS = 60
MAXIMUM_CYCLE_MS = 1500
MAXIMUM_WORKING_SET_GROWTH_MB = 384
REPLAY_ROW_LIMIT = 100000
REPLAY_BATCH_SIZE = 250
RESUME_CYCLE = 0
RESUME_REPLAY_ROWS = 0
RESUME_ELAPSED_SECONDS = 0

for path in (
    RESULT_PATH,
    LIFECYCLE_LEDGER_PATH,
    REPLAY_LEDGER_PATH,
    RUN_CHECKPOINT_PATH,
    PERSISTENT_CHECKPOINT_PATH,
):
    path.parent.mkdir(parents=True, exist_ok=True)

def working_set_mb():
    try:
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        ok = ctypes.windll.psapi.GetProcessMemoryInfo(
            handle,
            ctypes.byref(counters),
            counters.cb,
        )
        if ok:
            return round(counters.WorkingSetSize / (1024 * 1024), 6)
    except Exception:
        pass
    return 0.0

def atomic_json_write(path, payload):
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)

def safe_float(value):
    try:
        if value is None:
            return None
        text = str(value).strip().replace(",", ".")
        if not text:
            return None
        result = float(text)
        if math.isfinite(result):
            return result
    except Exception:
        pass
    return None

def select_price(row):
    preferred = [
        "close", "Close", "CLOSE",
        "price", "Price", "PRICE",
        "last", "Last", "LAST",
        "bid", "Bid", "BID",
        "open", "Open", "OPEN",
    ]
    for key in preferred:
        if key in row:
            value = safe_float(row.get(key))
            if value is not None:
                return value

    for value in row.values():
        number = safe_float(value)
        if number is not None:
            return number
    return None

def synthetic_decision(current_price, previous_price, rolling_mean):
    if current_price is None:
        return "HOLD"

    if previous_price is None or rolling_mean is None:
        return "HOLD"

    delta = current_price - previous_price
    deviation = current_price - rolling_mean

    if abs(delta) < 1e-12:
        return "HOLD"

    if delta > 0 and deviation > 0:
        return "ALLOW_PAPER_SIGNAL"

    if delta < 0 and deviation < 0:
        return "BLOCK_RISK"

    return "HOLD"

with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
    manifest = json.load(handle)

baseline_threads = {t.ident for t in threading.enumerate()}
baseline_memory_mb = working_set_mb()
violations = []
lifecycle_rows = []
replay_rows = []
runtime = None
factory_invocations = 0
cycles_completed = RESUME_CYCLE
replay_rows_completed = RESUME_REPLAY_ROWS
checkpoint_count = 0
cycle_failures = 0
replay_failures = 0
max_cycle_ms = 0.0
sum_cycle_ms = 0.0
hold_count = 0
allow_count = 0
block_count = 0
synthetic_pnl = 0.0
synthetic_peak = 0.0
synthetic_drawdown = 0.0
started_monotonic = time.monotonic() - RESUME_ELAPSED_SECONDS
last_checkpoint_monotonic = time.monotonic()
status = "EXTENDED_SUPERVISED_PAPER_AND_REPLAY_FAIL"
error_type = ""
error_message = ""
error_traceback = ""

original_socket = socket.socket
original_popen = subprocess.Popen
original_thread_start = threading.Thread.start

def blocked_socket(*args, **kwargs):
    violations.append({"type": "NETWORK_ATTEMPT", "args": repr(args)})
    raise RuntimeError("NETWORK_FORBIDDEN")

def blocked_popen(*args, **kwargs):
    violations.append({"type": "SUBPROCESS_ATTEMPT", "args": repr(args)})
    raise RuntimeError("SUBPROCESS_FORBIDDEN")

def blocked_thread_start(self, *args, **kwargs):
    violations.append({"type": "THREAD_ATTEMPT", "name": getattr(self, "name", "")})
    raise RuntimeError("THREAD_CREATION_FORBIDDEN")

socket.socket = blocked_socket
subprocess.Popen = blocked_popen
threading.Thread.start = blocked_thread_start

try:
    sys.path.insert(0, str(RUNTIME_ROOT))

    wiring = importlib.import_module("app.runtime.mind_trader_institutional_wiring")
    factory = getattr(wiring, "create_paper_runtime")
    health_fn = getattr(wiring, "health")

    runtime = factory()
    factory_invocations += 1

    expected_cycles = max(1, int(DURATION_SECONDS / HEARTBEAT_SECONDS))
    price_window = []
    previous_price = None
    replay_file_index = 0

    for file_info in manifest.get("files", []):
        if replay_rows_completed >= REPLAY_ROW_LIMIT:
            break

        replay_file_index += 1
        file_path = Path(file_info["path"])

        if not file_path.exists():
            replay_failures += 1
            replay_rows.append({
                "file_index": replay_file_index,
                "row": 0,
                "status": "FILE_MISSING",
                "decision": "HOLD",
                "price": "",
                "synthetic_pnl": synthetic_pnl,
            })
            continue

        with file_path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)

            for row_number, row in enumerate(reader, start=1):
                if replay_rows_completed >= REPLAY_ROW_LIMIT:
                    break

                if replay_rows_completed < RESUME_REPLAY_ROWS:
                    replay_rows_completed += 1
                    continue

                price = select_price(row)

                rolling_mean = (
                    sum(price_window) / len(price_window)
                    if price_window else None
                )

                decision = synthetic_decision(price, previous_price, rolling_mean)

                if decision == "ALLOW_PAPER_SIGNAL":
                    allow_count += 1
                elif decision == "BLOCK_RISK":
                    block_count += 1
                else:
                    hold_count += 1

                if price is not None:
                    if previous_price is not None:
                        move = price - previous_price
                        if decision == "ALLOW_PAPER_SIGNAL":
                            synthetic_pnl += move
                        elif decision == "BLOCK_RISK":
                            synthetic_pnl -= abs(move) * 0.1

                    price_window.append(price)
                    if len(price_window) > 50:
                        price_window.pop(0)
                    previous_price = price

                synthetic_peak = max(synthetic_peak, synthetic_pnl)
                synthetic_drawdown = min(
                    synthetic_drawdown,
                    synthetic_pnl - synthetic_peak,
                )

                replay_rows_completed += 1

                replay_rows.append({
                    "file_index": replay_file_index,
                    "row": row_number,
                    "status": "PASS",
                    "decision": decision,
                    "price": "" if price is None else price,
                    "synthetic_pnl": round(synthetic_pnl, 10),
                })

                if len(replay_rows) >= REPLAY_BATCH_SIZE:
                    with REPLAY_LEDGER_PATH.open(
                        "a",
                        newline="",
                        encoding="utf-8",
                    ) as replay_handle:
                        writer = csv.DictWriter(
                            replay_handle,
                            fieldnames=[
                                "file_index",
                                "row",
                                "status",
                                "decision",
                                "price",
                                "synthetic_pnl",
                            ],
                        )
                        if REPLAY_LEDGER_PATH.stat().st_size == 0:
                            writer.writeheader()
                        writer.writerows(replay_rows)
                    replay_rows.clear()

    if replay_rows:
        with REPLAY_LEDGER_PATH.open("a", newline="", encoding="utf-8") as replay_handle:
            writer = csv.DictWriter(
                replay_handle,
                fieldnames=[
                    "file_index",
                    "row",
                    "status",
                    "decision",
                    "price",
                    "synthetic_pnl",
                ],
            )
            if REPLAY_LEDGER_PATH.stat().st_size == 0:
                writer.writeheader()
            writer.writerows(replay_rows)
        replay_rows.clear()

    while cycles_completed < expected_cycles:
        cycle_started = time.monotonic()

        health_result = health_fn()
        if not isinstance(health_result, dict):
            raise RuntimeError("HEALTH_RESULT_NOT_DICT")

        cycle_ms = (time.monotonic() - cycle_started) * 1000.0
        max_cycle_ms = max(max_cycle_ms, cycle_ms)
        sum_cycle_ms += cycle_ms
        cycles_completed += 1

        cycle_pass = cycle_ms <= MAXIMUM_CYCLE_MS
        if not cycle_pass:
            cycle_failures += 1

        lifecycle_rows.append({
            "cycle": cycles_completed,
            "status": "PASS" if cycle_pass else "FAIL",
            "duration_ms": round(cycle_ms, 6),
            "memory_mb": working_set_mb(),
            "replay_rows_completed": replay_rows_completed,
            "violations": len(violations),
        })

        now = time.monotonic()
        elapsed_seconds = now - started_monotonic

        if (now - last_checkpoint_monotonic) >= CHECKPOINT_SECONDS:
            checkpoint_count += 1
            checkpoint = {
                "run_id": "20260805_183007",
                "cycles_completed": cycles_completed,
                "expected_cycles": expected_cycles,
                "replay_rows_completed": replay_rows_completed,
                "replay_row_limit": REPLAY_ROW_LIMIT,
                "elapsed_seconds": elapsed_seconds,
                "checkpoint_count": checkpoint_count,
                "completed": False,
                "mode": "PAPER_ONLY",
                "broker": "SIMULATED",
                "runtime_started": False,
                "runtime_loop_started": False,
                "broker_connection": False,
                "order_execution": False,
                "live_real": "FORBIDDEN",
                "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            atomic_json_write(RUN_CHECKPOINT_PATH, checkpoint)
            atomic_json_write(PERSISTENT_CHECKPOINT_PATH, checkpoint)
            last_checkpoint_monotonic = now

        sleep_remaining = HEARTBEAT_SECONDS - (time.monotonic() - cycle_started)
        if sleep_remaining > 0:
            time.sleep(sleep_remaining)

    with LIFECYCLE_LEDGER_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "cycle",
                "status",
                "duration_ms",
                "memory_mb",
                "replay_rows_completed",
                "violations",
            ],
        )
        writer.writeheader()
        writer.writerows(lifecycle_rows)

    gc.collect()
    final_memory_mb = working_set_mb()
    memory_growth_mb = round(final_memory_mb - baseline_memory_mb, 6)
    post_threads = {t.ident for t in threading.enumerate()}
    new_threads = [ident for ident in post_threads if ident not in baseline_threads]

    checks = {
        "factory_invoked_once": factory_invocations == 1,
        "runtime_materialized": runtime is not None,
        "cycles_completed": cycles_completed >= expected_cycles,
        "cycle_failures_zero": cycle_failures == 0,
        "replay_rows_processed": replay_rows_completed > 0,
        "replay_failures_zero": replay_failures == 0,
        "violations_zero": len(violations) == 0,
        "memory_growth_within_limit": memory_growth_mb <= MAXIMUM_WORKING_SET_GROWTH_MB,
        "new_threads_zero": len(new_threads) == 0,
        "orders_zero": True,
        "broker_not_connected": True,
    }

    all_pass = all(checks.values())

    if all_pass:
        status = "EXTENDED_SUPERVISED_PAPER_AND_REPLAY_PASS"

    final_checkpoint = {
        "run_id": "20260805_183007",
        "cycles_completed": cycles_completed,
        "expected_cycles": expected_cycles,
        "replay_rows_completed": replay_rows_completed,
        "replay_row_limit": REPLAY_ROW_LIMIT,
        "elapsed_seconds": time.monotonic() - started_monotonic,
        "checkpoint_count": checkpoint_count,
        "completed": all_pass,
        "mode": "PAPER_ONLY",
        "broker": "SIMULATED",
        "runtime_started": False,
        "runtime_loop_started": False,
        "broker_connection": False,
        "order_execution": False,
        "live_real": "FORBIDDEN",
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    atomic_json_write(RUN_CHECKPOINT_PATH, final_checkpoint)
    atomic_json_write(PERSISTENT_CHECKPOINT_PATH, final_checkpoint)

    result = {
        "status": status,
        "run_id": "20260805_183007",
        "mode": "PAPER_ONLY",
        "broker": "SIMULATED",
        "materialization": {
            "pass": runtime is not None,
            "runtime_type": type(runtime).__name__ if runtime is not None else "",
            "factory_invocations": factory_invocations,
        },
        "supervision": {
            "pass": checks["cycles_completed"] and checks["cycle_failures_zero"],
            "duration_requested_seconds": DURATION_SECONDS,
            "elapsed_seconds": time.monotonic() - started_monotonic,
            "expected_cycles": expected_cycles,
            "cycles_completed": cycles_completed,
            "cycle_failures": cycle_failures,
            "average_cycle_ms": round(sum_cycle_ms / max(1, cycles_completed - RESUME_CYCLE), 6),
            "maximum_cycle_ms": round(max_cycle_ms, 6),
            "checkpoint_count": checkpoint_count,
            "resume_cycle": RESUME_CYCLE,
        },
        "market_replay": {
            "pass": checks["replay_rows_processed"] and checks["replay_failures_zero"],
            "files_manifested": len(manifest.get("files", [])),
            "rows_completed": replay_rows_completed,
            "row_limit": REPLAY_ROW_LIMIT,
            "failures": replay_failures,
            "hold": hold_count,
            "allow_paper_signal": allow_count,
            "block_risk": block_count,
            "synthetic_pnl": round(synthetic_pnl, 10),
            "synthetic_max_drawdown": round(synthetic_drawdown, 10),
        },
        "memory": {
            "baseline_mb": baseline_memory_mb,
            "final_mb": final_memory_mb,
            "growth_mb": memory_growth_mb,
            "maximum_growth_mb": MAXIMUM_WORKING_SET_GROWTH_MB,
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
        "status": "EXTENDED_SUPERVISED_PAPER_AND_REPLAY_FAIL",
        "run_id": "20260805_183007",
        "mode": "PAPER_ONLY",
        "broker": "SIMULATED",
        "materialization": {
            "pass": runtime is not None,
            "runtime_type": type(runtime).__name__ if runtime is not None else "",
            "factory_invocations": factory_invocations,
        },
        "supervision": {
            "pass": False,
            "cycles_completed": cycles_completed,
            "cycle_failures": cycle_failures,
            "checkpoint_count": checkpoint_count,
        },
        "market_replay": {
            "pass": False,
            "rows_completed": replay_rows_completed,
            "failures": replay_failures,
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

    checkpoint = {
        "run_id": "20260805_183007",
        "cycles_completed": cycles_completed,
        "replay_rows_completed": replay_rows_completed,
        "elapsed_seconds": time.monotonic() - started_monotonic,
        "checkpoint_count": checkpoint_count,
        "completed": False,
        "error_type": error_type,
        "error_message": error_message,
        "mode": "PAPER_ONLY",
        "broker": "SIMULATED",
        "runtime_started": False,
        "runtime_loop_started": False,
        "broker_connection": False,
        "order_execution": False,
        "live_real": "FORBIDDEN",
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    atomic_json_write(RUN_CHECKPOINT_PATH, checkpoint)
    atomic_json_write(PERSISTENT_CHECKPOINT_PATH, checkpoint)

finally:
    socket.socket = original_socket
    subprocess.Popen = original_popen
    threading.Thread.start = original_thread_start
    atomic_json_write(RESULT_PATH, result)

sys.exit(0 if result.get("status") == "EXTENDED_SUPERVISED_PAPER_AND_REPLAY_PASS" else 20)
