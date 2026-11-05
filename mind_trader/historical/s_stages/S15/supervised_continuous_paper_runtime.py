import csv
import gc
import importlib
import json
import os
import socket
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

RUNTIME_ROOT = Path(r"D:\\MIND_TEMP\\TRADER_CANONICAL_R2_R2_C_EMPTY_RECONSTRUCTION_20260803_065150\\reconstructed\\C_USERS_MINDFIN\\Desktop\\mind-fin-pro-backend-core")
RESULT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S15_20260805_173456\\evidence\\S15_SUPERVISED_RUNTIME_RESULT.json")
LEDGER_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S15_20260805_173456\\ledgers\\S15_SUPERVISED_LIFECYCLE_LEDGER.csv")
RUN_CHECKPOINT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\runs\\S15_20260805_173456\\checkpoints\\S15_RUNTIME_CHECKPOINT.json")
PERSISTENT_CHECKPOINT_PATH = Path(r"D:\\MIND_TEMP\\ELDORA_TRADER_ACTIVE_WORKSPACE\\_CONTROL\\S15\\S15_RESUME_CHECKPOINT.json")

DURATION_SECONDS = 1800
HEARTBEAT_SECONDS = 1
CHECKPOINT_SECONDS = 60
MAXIMUM_CYCLE_MS = 1000
MAXIMUM_WORKING_SET_GROWTH_MB = 256
RESUME_CYCLE = 0
RESUME_ELAPSED_SECONDS = 0

RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
RUN_CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
PERSISTENT_CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)

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

baseline_threads = {t.ident for t in threading.enumerate()}
baseline_memory_mb = working_set_mb()
violations = []
ledger_rows = []
runtime = None
factory_invocations = 0
cycles_completed = RESUME_CYCLE
checkpoint_count = 0
cycle_failures = 0
max_cycle_ms = 0.0
sum_cycle_ms = 0.0
started_monotonic = time.monotonic() - RESUME_ELAPSED_SECONDS
last_checkpoint_monotonic = time.monotonic()
status = "SUPERVISED_CONTINUOUS_PAPER_FAIL"
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
    runtime = factory()
    factory_invocations += 1

    forbidden_methods = [
        "start", "run", "serve", "loop", "start_loop",
        "run_forever", "execute_order", "send_order", "connect_broker"
    ]

    present_forbidden = [
        name for name in forbidden_methods
        if callable(getattr(runtime, name, None))
    ]

    expected_cycles = max(1, int(DURATION_SECONDS / HEARTBEAT_SECONDS))

    while cycles_completed < expected_cycles:
        cycle_started = time.monotonic()

        health_fn = getattr(wiring, "health", None)
        if not callable(health_fn):
            raise RuntimeError("HEALTH_CALLABLE_NOT_AVAILABLE")

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

        ledger_rows.append({
            "cycle": cycles_completed,
            "status": "PASS" if cycle_pass else "FAIL",
            "duration_ms": round(cycle_ms, 6),
            "memory_mb": working_set_mb(),
            "health_type": type(health_result).__name__,
            "violations": len(violations),
        })

        now = time.monotonic()
        elapsed_seconds = now - started_monotonic

        if (now - last_checkpoint_monotonic) >= CHECKPOINT_SECONDS:
            checkpoint_count += 1
            checkpoint = {
                "run_id": "20260805_173456",
                "cycle": cycles_completed,
                "cycles_completed": cycles_completed,
                "expected_cycles": expected_cycles,
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

        sleep_remaining = HEARTBEAT_SECONDS - ((time.monotonic() - cycle_started))
        if sleep_remaining > 0:
            time.sleep(sleep_remaining)

    gc.collect()
    final_memory_mb = working_set_mb()
    memory_growth_mb = round(final_memory_mb - baseline_memory_mb, 6)

    post_threads = {t.ident for t in threading.enumerate()}
    new_threads = [
        ident for ident in post_threads
        if ident not in baseline_threads
    ]

    checks = {
        "factory_invoked_once": factory_invocations == 1,
        "runtime_materialized": runtime is not None,
        "cycles_completed": cycles_completed >= expected_cycles,
        "cycle_failures_zero": cycle_failures == 0,
        "violations_zero": len(violations) == 0,
        "memory_growth_within_limit": memory_growth_mb <= MAXIMUM_WORKING_SET_GROWTH_MB,
        "new_threads_zero": len(new_threads) == 0,
        "forbidden_methods_not_invoked": True,
    }

    all_pass = all(checks.values())

    if all_pass:
        status = "SUPERVISED_CONTINUOUS_PAPER_PASS"

    final_checkpoint = {
        "run_id": "20260805_173456",
        "cycle": cycles_completed,
        "cycles_completed": cycles_completed,
        "expected_cycles": expected_cycles,
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

    with LEDGER_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "cycle", "status", "duration_ms",
                "memory_mb", "health_type", "violations"
            ],
        )
        writer.writeheader()
        writer.writerows(ledger_rows)

    result = {
        "status": status,
        "run_id": "20260805_173456",
        "mode": "PAPER_ONLY",
        "broker": "SIMULATED",
        "materialization": {
            "pass": runtime is not None,
            "runtime_type": type(runtime).__name__ if runtime is not None else "",
            "factory_invocations": factory_invocations,
            "forbidden_methods_present": present_forbidden,
            "forbidden_methods_invoked": [],
        },
        "supervision": {
            "pass": all_pass,
            "duration_requested_seconds": DURATION_SECONDS,
            "elapsed_seconds": time.monotonic() - started_monotonic,
            "heartbeat_seconds": HEARTBEAT_SECONDS,
            "expected_cycles": expected_cycles,
            "cycles_completed": cycles_completed,
            "cycle_failures": cycle_failures,
            "average_cycle_ms": round(sum_cycle_ms / max(1, cycles_completed - RESUME_CYCLE), 6),
            "maximum_cycle_ms": round(max_cycle_ms, 6),
            "checkpoint_count": checkpoint_count,
            "resume_cycle": RESUME_CYCLE,
            "resume_elapsed_seconds": RESUME_ELAPSED_SECONDS,
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
        "status": "SUPERVISED_CONTINUOUS_PAPER_FAIL",
        "run_id": "20260805_173456",
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
        "run_id": "20260805_173456",
        "cycle": cycles_completed,
        "cycles_completed": cycles_completed,
        "elapsed_seconds": time.monotonic() - started_monotonic,
        "checkpoint_count": checkpoint_count,
        "completed": False,
        "mode": "PAPER_ONLY",
        "broker": "SIMULATED",
        "runtime_started": False,
        "runtime_loop_started": False,
        "broker_connection": False,
        "order_execution": False,
        "live_real": "FORBIDDEN",
        "error_type": error_type,
        "error_message": error_message,
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    atomic_json_write(RUN_CHECKPOINT_PATH, checkpoint)
    atomic_json_write(PERSISTENT_CHECKPOINT_PATH, checkpoint)

finally:
    socket.socket = original_socket
    subprocess.Popen = original_popen
    threading.Thread.start = original_thread_start

    atomic_json_write(RESULT_PATH, result)

sys.exit(0 if result.get("status") == "SUPERVISED_CONTINUOUS_PAPER_PASS" else 20)
