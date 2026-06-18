from __future__ import annotations
import time

class RuntimeMetrics:
    def snapshot(self,metrics:dict|None=None):
        metrics=metrics or {}

        return {
            "timestamp":time.time(),
            "runtime_status":metrics.get("runtime_status","ONLINE"),
            "modules":metrics.get("modules",0),
            "tests":metrics.get("tests",0),
            "experiments":metrics.get("experiments",0),
            "evidence":metrics.get("evidence",0)
        }
