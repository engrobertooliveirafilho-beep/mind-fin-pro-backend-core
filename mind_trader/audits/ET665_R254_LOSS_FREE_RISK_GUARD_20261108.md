# ET665.R254 — Loss-free sample risk guard

Date: 2026-11-08. Scope: draft PR #18, P15.25.

## Finding
R253 corrected the zero-trade case, but a sample with one or more wins and no observed loss still produced `profit_factor=99` and `risk_proxy=LOW`. No observed loss does not establish low risk; the finite loss denominator required for a profit-factor estimate is absent.

## Patch and regression
The proxy now returns `UNKNOWN` and null profit factor whenever no losses are observed, including all-win and flat samples. Four offline tests cover single win, 100 wins, flat returns, and finite mixed outcomes.

## Evidence boundary
Code and tests published, **not executed**. This does not prove calibrated risk-of-ruin estimation. CI, Docker, R113 integration, R60 reconciliation, MT5 isolation and independent review remain unproven. Draft PR only; no merge, production or real orders. FASE_B=0/16 | HP19=0/19 | COST=R$0.
