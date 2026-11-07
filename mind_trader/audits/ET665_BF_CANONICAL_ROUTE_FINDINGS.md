# ET665.BF — Exact GitHub path reconciliation and targeted execution security review

Date: 2026-11-06. Code ref inspected: `37b363a0316769097a551c787513d2bbb7f08254`. Read-only inspection; no MT5 connection or order transmission attempted.

The operator's ET665.BE staging contains 21 Python files; 66 of 74 inventory references were not found there. This is a staging-coverage issue, **not evidence of 66 missing GitHub files**. Five paths below were fetched at the exact audited commit.

| Inventory path | GitHub blob SHA | Evidence and classification |
|---|---|---|
| `mind_trader/app/p69_73_mt5_ftmo_demo_governor/engine.py` | `99fe2a3607368e67a4a8c8e599ed96906fb7b010` | Present. DEMO-only policy returns, synthetic FTMO simulator. Not an authenticated MT5 broker gate. |
| `mind_trader/app/p74_mt5_demo_order_router_dry_run/engine.py` | `003d1480f4ee9c1c557d35d5d344e005f77a5e42` | Present. `route_order_dry_run` sets `sent_to_mt5=False`, `real_order_sent=False`; no transmission call observed. |
| `mind_trader/app/p75_mt5_demo_order_execution_controlled/engine.py` | `41ca445bbc9751837b4697200afe278a9d40284e` | Present. `EXECUTION_ARMED=False` by default. If armed and confirmed, `sent_to_mt5_demo` is assigned the boolean `allowed` without an MT5 send call. **Misleading claimed-send state**, not evidence of real send. Keep unarmed. |
| `mind_trader/app/p86_execution_intelligence_domain/engine.py` | `da3206080bd1c5a5942d1f398579c1eedad4649c` | Present. Imports `MetaTrader5`; `mt5_snapshot` calls `mt5.initialize`, `account_info`, `terminal_info`, `positions_get`, `symbol_select`, `symbol_info_tick`, `shutdown`. No `order_send` observed in this file. **External terminal connectivity/read access**; exclude from unisolated tests and require explicit account-mode/transport gate. |
| `mind_trader/app/validation/promotion_authority.py` | `071b9e7018b6e0392a3392572de5721d18b25981` | Present. Forbids four exact target strings, but other unknown targets can pass when `validation_result.decision=PAPER_TRADING_APPROVED`. **Fail-open target allowlist gap**; require positive PAPER-only allowlist, normalized type checking, negative tests. |

## Priority controls
1. P86: enforce offline import/simulation-only testing and verified DEMO account/terminal state before any optional MT5 connectivity; inspect all callers and import side effects.
2. P75: separate `permission_granted` from `order_sent`; never report actual transmission without a transport acknowledgment. Keep execution disabled.
3. Promotion authority: explicit allowlist, reject unknown/non-string target values and preserve PAPER-only semantics.
4. Do not assume P69–P75 and P86 are covered by the 45-test ET665.BB suite.
5. Reconcile remaining 61 inventory occurrences by exact GitHub path. Repeated CSV rows must be evaluated at their distinct source lines.

No production or live actions authorized. `PHASE_B=OPEN`, `SECURITY_APPROVAL=NOT_GRANTED`, `REAL_ORDERS=FORBIDDEN`.
