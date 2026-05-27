
import os, json, time
LAST_CANARY_TRACE={}

def trace_canary(sender, message, enabled, percent, allowlist, decision, branch):
    global LAST_CANARY_TRACE
    LAST_CANARY_TRACE={
        "ts":time.time(),
        "sender":sender,
        "message":message,
        "env_enabled":enabled,
        "env_percent":percent,
        "env_allowlist":allowlist,
        "decision":decision,
        "branch":branch
    }
    return LAST_CANARY_TRACE

def get_last_canary_trace():
    return LAST_CANARY_TRACE
