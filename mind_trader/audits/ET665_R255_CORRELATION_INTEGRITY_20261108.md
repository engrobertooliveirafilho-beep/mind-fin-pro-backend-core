# ET665.R255 — Correlation evidence integrity

Date: 2026-11-08. Draft PR #18; P15.25 research.

## Source finding
The correlation helper truncated unequal return sequences to their shorter length, reporting a coefficient as though samples were aligned. It also reported zero correlation for fewer than three samples and for zero-variance inputs, when Pearson correlation is undefined. Nonfinite values were not explicitly rejected.

## Change
Unequal sample lengths and invalid/nonfinite returns now raise `ValueError`. Insufficient observations and zero-variance samples return JSON-compatible `null` (Python `None`). Finite equal-length samples retain Pearson calculation. Five offline regressions were published.

## Residual limitation
Equal lengths do **not** establish timestamp alignment; this remains an unresolved structural limitation requiring timestamped trade series. The patch may surface previously masked data mismatches. No tests executed, CI/Docker PASS, independent approval or certification is claimed. PR draft, no merge or production change; REAL_ORDERS=FORBIDDEN, FTMO_REAL=FORBIDDEN, FASE_B=0/16, HP19=0/19, COST=R$0.
