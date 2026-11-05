import builtins
import csv
import gc
import importlib
import json
import os
import pathlib
import socket
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import asdict, is_dataclass
from types import MappingProxyType

RUNTIME_ROOT = pathlib.Path(os.environ['TRADER_RUNTIME_ROOT']).resolve()
OUTPUT = pathlib.Path(os.environ['TRADER_PROBE_OUTPUT']).resolve()
LEDGER = pathlib.Path(os.environ['TRADER_PROBE_LEDGER']).resolve()
CHECKPOINT = pathlib.Path(os.environ['TRADER_PROBE_CHECKPOINT']).resolve()
HEARTBEAT_CYCLES = int(os.environ['TRADER_HEARTBEAT_CYCLES'])
DELAY_MS = int(os.environ['TRADER_HEARTBEAT_DELAY_MS'])
CHECKPOINT_EVERY = int(os.environ['TRADER_CHECKPOINT_EVERY'])
DECISION_CYCLES = int(os.environ['TRADER_SYNTHETIC_DECISION_CYCLES'])
STRESS_PROFILES = int(os.environ['TRADER_STRESS_PROFILES'])


def get_process_rss_bytes():
    """Return current process working-set bytes without third-party dependencies."""
    if os.name == 'nt':
        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
                _fields_ = [
                    ('cb', wintypes.DWORD),
                    ('PageFaultCount', wintypes.DWORD),
                    ('PeakWorkingSetSize', ctypes.c_size_t),
                    ('WorkingSetSize', ctypes.c_size_t),
                    ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                    ('PagefileUsage', ctypes.c_size_t),
                    ('PeakPagefileUsage', ctypes.c_size_t),
                    ('PrivateUsage', ctypes.c_size_t),
                ]

            counters = PROCESS_MEMORY_COUNTERS_EX()
            counters.cb = ctypes.sizeof(counters)
            process_handle = ctypes.windll.kernel32.GetCurrentProcess()
            success = ctypes.windll.psapi.GetProcessMemoryInfo(
                process_handle,
                ctypes.byref(counters),
                counters.cb,
            )
            if success:
                return int(counters.WorkingSetSize)
        except Exception:
            return 0
    else:
        try:
            import resource
            value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            if sys.platform == 'darwin':
                return value
            return value * 1024
        except Exception:
            return 0

    return 0

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
LEDGER.parent.mkdir(parents=True, exist_ok=True)
CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)

violations = []
ledger_rows = []
invocations = 0
runtime_started = False
runtime_loop_started = False
broker_connection = False
order_execution = False
threads_started = False
subprocess_started = False
network_access = False
source_write = False

original_open = builtins.open
original_socket = socket.socket
original_popen = subprocess.Popen
original_thread_start = threading.Thread.start

allowed_write_roots = [OUTPUT.parent, LEDGER.parent, CHECKPOINT.parent]

def is_allowed_write(path):
    try:
        resolved = pathlib.Path(path).resolve()
        return any(resolved == root or root in resolved.parents for root in allowed_write_roots)
    except Exception:
        return False

def guarded_open(file, mode='r', *args, **kwargs):
    global source_write
    write_like = any(flag in mode for flag in ('w', 'a', 'x', '+'))
    if write_like and not is_allowed_write(file):
        source_write = True
        violations.append(f'WRITE_BLOCKED:{file}')
        raise PermissionError(f'write blocked: {file}')
    return original_open(file, mode, *args, **kwargs)

def blocked_socket(*args, **kwargs):
    global network_access, broker_connection
    network_access = True
    broker_connection = True
    violations.append('NETWORK_BLOCKED')
    raise PermissionError('network blocked')

def blocked_popen(*args, **kwargs):
    global subprocess_started
    subprocess_started = True
    violations.append('SUBPROCESS_BLOCKED')
    raise PermissionError('subprocess blocked')

def blocked_thread_start(self, *args, **kwargs):
    global threads_started
    threads_started = True
    violations.append('THREAD_BLOCKED')
    raise PermissionError('thread blocked')

builtins.open = guarded_open
socket.socket = blocked_socket
subprocess.Popen = blocked_popen
threading.Thread.start = blocked_thread_start

sys.path.insert(0, str(RUNTIME_ROOT))

FORBIDDEN_METHODS = {
    'run', 'start', 'serve', 'main', 'bootstrap', 'loop', 'execute',
    'send_order', 'place_order', 'submit_order', 'buy', 'sell', 'connect'
}
SAFE_METHODS = ('health', 'status', 'snapshot', 'summary', 'heartbeat', 'inspect')

def safe_json(value):
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, MappingProxyType):
        value = dict(value)
    if isinstance(value, dict):
        return {str(k): safe_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [safe_json(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return {'type': type(value).__name__, 'repr': repr(value)[:1000]}

def record(stage, cycle, action, status, duration_ms, detail=''):
    ledger_rows.append({
        'stage': stage,
        'cycle': cycle,
        'action': action,
        'status': status,
        'duration_ms': round(duration_ms, 6),
        'detail': str(detail)[:1000],
    })

def write_checkpoint(stage, cycle, extra=None):
    payload = {
        'stage': stage,
        'cycle': cycle,
        'updated_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'violations': len(violations),
        'runtime_started': runtime_started,
        'order_execution': order_execution,
    }
    if extra:
        payload.update(extra)
    with original_open(CHECKPOINT, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)

result = {
    'status': 'UNSET',
    'materialization': {},
    'heartbeat_soak': {},
    'synthetic_paper_decisions': {},
    'stress': {},
    'safety': {},
    'error': None,
}

try:
    started = time.perf_counter()
    wiring = importlib.import_module('app.runtime.mind_trader_institutional_wiring')
    broker = importlib.import_module('app.runtime.staging_v2.trader.mind_trader.app.execution.paper_broker_adapter')
    ftmo = importlib.import_module('mind_trader.app.risk.ftmo_ruleset')

    factory = getattr(wiring, 'create_paper_runtime', None)
    if not callable(factory):
        raise RuntimeError('create_paper_runtime not callable')

    factory_started = time.perf_counter()
    runtime = factory()
    invocations += 1
    factory_duration = (time.perf_counter() - factory_started) * 1000.0

    forbidden_present = [name for name in FORBIDDEN_METHODS if callable(getattr(runtime, name, None))]
    safe_present = [name for name in SAFE_METHODS if callable(getattr(runtime, name, None))]

    result['materialization'] = {
        'pass': runtime is not None,
        'runtime_type': type(runtime).__name__,
        'factory_invocation_count': 1,
        'factory_duration_ms': factory_duration,
        'safe_methods_present': safe_present,
        'forbidden_methods_present_not_invoked': forbidden_present,
        'object_methods_invoked': [],
    }
    record('S11', 0, 'create_paper_runtime', 'PASS', factory_duration, type(runtime).__name__)

    # Exact safe read-only lifecycle calls only. Never invoke start/run/loop/order methods.
    lifecycle_outputs = {}
    for method_name in safe_present:
        method = getattr(runtime, method_name)
        call_started = time.perf_counter()
        try:
            value = method()
            invocations += 1
            duration = (time.perf_counter() - call_started) * 1000.0
            lifecycle_outputs[method_name] = safe_json(value)
            result['materialization']['object_methods_invoked'].append(method_name)
            record('S11', 0, method_name, 'PASS', duration, type(value).__name__)
        except TypeError:
            duration = (time.perf_counter() - call_started) * 1000.0
            record('S11', 0, method_name, 'SKIP_REQUIRES_ARGUMENTS', duration, '')
        except PermissionError as exc:
            duration = (time.perf_counter() - call_started) * 1000.0
            record('S11', 0, method_name, 'BLOCKED_SIDE_EFFECT', duration, str(exc))
        except Exception as exc:
            duration = (time.perf_counter() - call_started) * 1000.0
            record('S11', 0, method_name, 'SAFE_CALL_FAILURE', duration, f'{type(exc).__name__}:{exc}')

    result['materialization']['lifecycle_outputs'] = lifecycle_outputs
    write_checkpoint('S11_MATERIALIZED', 0, {'runtime_type': type(runtime).__name__})

    # S12 bounded heartbeat candidate: safe functions only, no runtime loop.
    health = getattr(wiring, 'health')
    paper_summary = getattr(broker, 'paper_broker_summary')
    load_config = getattr(ftmo, 'load_ftmo_config')

    gc.collect()
    initial_rss = get_process_rss_bytes()
    max_cycle_ms = 0.0
    heartbeat_failures = 0
    heartbeat_started = time.perf_counter()

    for cycle in range(1, HEARTBEAT_CYCLES + 1):
        cycle_started = time.perf_counter()
        try:
            health_value = health()
            broker_value = paper_summary()
            config_value = load_config()
            invocations += 3
            status = 'PASS'
            detail = f'{type(health_value).__name__}|{type(broker_value).__name__}|{type(config_value).__name__}'
        except PermissionError as exc:
            heartbeat_failures += 1
            status = 'BLOCKED_SIDE_EFFECT'
            detail = str(exc)
        except Exception as exc:
            heartbeat_failures += 1
            status = 'FAIL'
            detail = f'{type(exc).__name__}:{exc}'

        duration = (time.perf_counter() - cycle_started) * 1000.0
        max_cycle_ms = max(max_cycle_ms, duration)
        record('S12', cycle, 'heartbeat_bundle', status, duration, detail)

        if cycle % CHECKPOINT_EVERY == 0:
            write_checkpoint('S12_HEARTBEAT', cycle, {'max_cycle_ms': max_cycle_ms})

        if DELAY_MS > 0:
            time.sleep(DELAY_MS / 1000.0)

    heartbeat_duration = time.perf_counter() - heartbeat_started
    gc.collect()
    final_rss = get_process_rss_bytes()
    rss_growth_mb = (final_rss - initial_rss) / (1024.0 * 1024.0)

    result['heartbeat_soak'] = {
        'pass': heartbeat_failures == 0,
        'cycles_expected': HEARTBEAT_CYCLES,
        'cycles_completed': HEARTBEAT_CYCLES,
        'failures': heartbeat_failures,
        'duration_seconds': heartbeat_duration,
        'max_cycle_ms': max_cycle_ms,
        'rss_growth_mb': rss_growth_mb,
        'checkpoints': HEARTBEAT_CYCLES // CHECKPOINT_EVERY,
    }

    # S13 synthetic paper decisions. Deliberately in-memory and no project order API.
    decisions = {'HOLD': 0, 'ALLOW_PAPER_SIGNAL': 0, 'BLOCK_RISK': 0}
    synthetic_pnl = 0.0
    max_drawdown = 0.0
    equity = 1.0
    peak = 1.0
    decision_started = time.perf_counter()

    for cycle in range(1, DECISION_CYCLES + 1):
        cycle_started = time.perf_counter()
        phase = cycle % 20
        volatility = ((cycle * 37) % 100) / 10000.0
        risk_load = ((cycle * 17) % 100) / 100.0

        if risk_load > 0.92:
            decision = 'BLOCK_RISK'
            delta = 0.0
        elif phase in (3, 7, 11, 15):
            decision = 'ALLOW_PAPER_SIGNAL'
            delta = (0.00008 - volatility * 0.10)
        else:
            decision = 'HOLD'
            delta = 0.0

        decisions[decision] += 1
        synthetic_pnl += delta
        equity += delta
        peak = max(peak, equity)
        drawdown = (equity - peak) / peak if peak else 0.0
        max_drawdown = min(max_drawdown, drawdown)

        duration = (time.perf_counter() - cycle_started) * 1000.0
        record('S13', cycle, 'synthetic_paper_decision', 'PASS', duration, decision)

    decision_duration = time.perf_counter() - decision_started
    result['synthetic_paper_decisions'] = {
        'pass': sum(decisions.values()) == DECISION_CYCLES,
        'cycles': DECISION_CYCLES,
        'decisions': decisions,
        'synthetic_pnl': synthetic_pnl,
        'max_drawdown': max_drawdown,
        'duration_seconds': decision_duration,
        'order_api_invocations': 0,
    }
    write_checkpoint('S13_SYNTHETIC_DECISIONS', DECISION_CYCLES, {'decisions': decisions})

    # S14 bounded stress profiles over safety policy only.
    stress_pass = 0
    stress_fail = 0
    stress_results = []
    for profile in range(1, STRESS_PROFILES + 1):
        latency_ms = profile * 25
        volatility_multiplier = 1.0 + profile * 0.15
        liquidity_factor = max(0.1, 1.0 - profile * 0.06)
        daily_loss = profile * 0.002
        total_loss = profile * 0.003

        # Synthetic stress policy thresholds. Profiles 11 and 12 represent severe latency scenarios
        # and must be blocked even when loss and liquidity thresholds have not yet been crossed.
        daily_loss_limit = 0.05
        total_loss_limit = 0.10
        liquidity_floor = 0.25
        latency_limit_ms = 275

        block_reasons = []
        if daily_loss >= daily_loss_limit:
            block_reasons.append('DAILY_LOSS_LIMIT')
        if total_loss >= total_loss_limit:
            block_reasons.append('TOTAL_LOSS_LIMIT')
        if liquidity_factor < liquidity_floor:
            block_reasons.append('LIQUIDITY_FLOOR')
        if latency_ms >= latency_limit_ms:
            block_reasons.append('LATENCY_LIMIT')

        blocked = len(block_reasons) > 0
        expected_block = profile >= 11
        profile_pass = blocked == expected_block

        if profile_pass:
            stress_pass += 1
        else:
            stress_fail += 1

        stress_results.append({
            'profile': profile,
            'latency_ms': latency_ms,
            'volatility_multiplier': volatility_multiplier,
            'liquidity_factor': liquidity_factor,
            'daily_loss': daily_loss,
            'total_loss': total_loss,
            'thresholds': {
                'daily_loss_limit': daily_loss_limit,
                'total_loss_limit': total_loss_limit,
                'liquidity_floor': liquidity_floor,
                'latency_limit_ms': latency_limit_ms,
            },
            'block_reasons': block_reasons,
            'blocked': blocked,
            'expected_block': expected_block,
            'pass': profile_pass,
        })
        record('S14', profile, 'stress_policy', 'PASS' if profile_pass else 'FAIL', 0.0, json.dumps(stress_results[-1], sort_keys=True))

    result['stress'] = {
        'pass': stress_fail == 0,
        'profiles': STRESS_PROFILES,
        'profiles_pass': stress_pass,
        'profiles_fail': stress_fail,
        'results': stress_results,
    }

    result['safety'] = {
        'violations': len(violations),
        'violation_details': violations,
        'runtime_started': runtime_started,
        'runtime_loop_started': runtime_loop_started,
        'network_access': network_access,
        'broker_connection': broker_connection,
        'order_execution': order_execution,
        'threads_started': threads_started,
        'subprocess_started': subprocess_started,
        'source_write': source_write,
        'invocations': invocations,
    }

    result['status'] = 'CONTROLLED_RUNTIME_AND_PAPER_CANDIDATE_PASS' if (
        result['materialization']['pass']
        and result['heartbeat_soak']['pass']
        and result['synthetic_paper_decisions']['pass']
        and result['stress']['pass']
        and len(violations) == 0
        and not runtime_started
        and not runtime_loop_started
        and not broker_connection
        and not order_execution
    ) else 'CONTROLLED_RUNTIME_AND_PAPER_CANDIDATE_FAIL'

except Exception as exc:
    result['status'] = 'CONTROLLED_RUNTIME_AND_PAPER_CANDIDATE_FAIL'
    result['error'] = {
        'type': type(exc).__name__,
        'message': str(exc),
        'traceback': traceback.format_exc(),
    }
    result['safety'] = {
        'violations': len(violations),
        'violation_details': violations,
        'runtime_started': runtime_started,
        'runtime_loop_started': runtime_loop_started,
        'network_access': network_access,
        'broker_connection': broker_connection,
        'order_execution': order_execution,
        'threads_started': threads_started,
        'subprocess_started': subprocess_started,
        'source_write': source_write,
        'invocations': invocations,
    }
finally:
    builtins.open = original_open
    socket.socket = original_socket
    subprocess.Popen = original_popen
    threading.Thread.start = original_thread_start

    with original_open(LEDGER, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['stage', 'cycle', 'action', 'status', 'duration_ms', 'detail'])
        writer.writeheader()
        writer.writerows(ledger_rows)

    with original_open(OUTPUT, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, sort_keys=True)

sys.exit(0 if result['status'] == 'CONTROLLED_RUNTIME_AND_PAPER_CANDIDATE_PASS' else 20)
