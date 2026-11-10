"""ET665.R344 — explicitly isolated adapter for ONE real cashflow component.

This is NOT an HP19 agent implementation and cannot certify 19/19.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SOURCE = Path(__file__).with_name("et665_r343_cashflow.py")

def run_component(payload):
    spec = spec_from_file_location("et665_r344_cashflow", SOURCE)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run_dry(payload)
    if (result.get("agent_id") != "business.strategy_cashflow_agent"
        or result.get("status") != "processed"
        or result.get("mode") != "paper_only"
        or result.get("real_orders") != "FORBIDDEN"
        or result.get("promotion_authorized") is not False):
        raise RuntimeError("fail-closed: invalid cashflow component result")
    return result
