"""ET665: independent financial units/risk gate for offline PAPER only.

Amounts: prices and commission per unit in quote currency; risk in account
currency. No implicit FX, contract multiplier, or lot convention.
"""
import math


def verify_paper_financial_contract(*, side, entry_fill, stop, quantity,
                                    quote_to_account_rate, contract_multiplier,
                                    commission_per_unit_per_side, spread,
                                    slippage, reserved_risk_account,
                                    tolerance=1e-8):
    blocked={"decision":"BLOCK_FINANCIAL_CONTRACT","production":"BLOCKED",
             "real_broker_routing":"DISABLED"}
    if side not in ("BUY","SELL"):
        return dict(blocked,reason="INVALID_SIDE")
    values=(entry_fill,stop,quantity,quote_to_account_rate,contract_multiplier,
            reserved_risk_account)
    costs=(commission_per_unit_per_side,spread,slippage)
    if any(type(v) not in (int,float) or not math.isfinite(v) or v <= 0 for v in values):
        return dict(blocked,reason="INVALID_POSITIVE_UNITS")
    if any(type(v) not in (int,float) or not math.isfinite(v) or v < 0 for v in costs):
        return dict(blocked,reason="INVALID_COSTS")
    if (side=="BUY" and stop>=entry_fill) or (side=="SELL" and stop<=entry_fill):
        return dict(blocked,reason="INVALID_STOP_DIRECTION")
    # Stop price is the unadjusted historical trigger; exit spread/slippage
    # and round-trip commissions are part of account-currency loss.
    friction=spread/2+slippage
    exit_fill=stop-friction if side=="BUY" else stop+friction
    if exit_fill<=0:
        return dict(blocked,reason="INVALID_ADVERSE_EXIT_FILL")
    adverse=(entry_fill-exit_fill if side=="BUY" else exit_fill-entry_fill)
    loss_account=(adverse+2*commission_per_unit_per_side)*quantity*contract_multiplier*quote_to_account_rate
    if not math.isfinite(loss_account) or loss_account<=0:
        return dict(blocked,reason="INVALID_COMPUTED_LOSS")
    # Reserving LESS than expected stop loss is unsafe. Extra reserve is safe,
    # but must be visible and never represented as exact sizing.
    if reserved_risk_account + tolerance < loss_account:
        return dict(blocked,reason="UNDER_RESERVED_STOP_LOSS",
                    expected_stop_loss_account=loss_account,
                    reserved_risk_account=reserved_risk_account)
    return {"decision":"FINANCIAL_CONTRACT_VALIDATED",
            "production":"BLOCKED","real_broker_routing":"DISABLED",
            "expected_stop_loss_account":loss_account,
            "reserved_risk_account":reserved_risk_account,
            "reserve_headroom_account":reserved_risk_account-loss_account,
            "quantity_units":quantity,"contract_multiplier":contract_multiplier,
            "quote_to_account_rate":quote_to_account_rate}
