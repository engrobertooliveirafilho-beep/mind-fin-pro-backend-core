"""ET667 DERIVED compatibility facade. NOT the original historical runtime.
No broker, no network, no order dispatch. This module is an interface probe only.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class HistoricalPaperRuntime:
    mode: str = "PAPER_ONLY"
    runtime_started: bool = False
    broker_connection: bool = False
    order_execution: bool = False

    def health(self):
        return {"status": "COMPATIBILITY_ONLY", "mode": self.mode,
                "runtime_started": self.runtime_started,
                "broker_connection": self.broker_connection,
                "order_execution": self.order_execution,
                "historical_runtime_recovered": False}

def create_paper_runtime():
    return HistoricalPaperRuntime()

def health():
    return create_paper_runtime().health()
