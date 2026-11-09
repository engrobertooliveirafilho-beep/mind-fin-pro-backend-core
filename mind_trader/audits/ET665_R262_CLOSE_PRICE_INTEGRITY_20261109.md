# ET665.R262 — Required close-price integrity

Date: 2026-11-09. Draft PR #18.

## Finding
The CSV loader used `r.get("close",0)` and silently filtered nonpositive values. Missing `close` headers and zero/negative close prices could therefore be interpreted as empty/shortened valid data, affecting strategy reconstruction.

## Patch
Require the `close` header, parse each row exactly once, and reject missing/nonfinite/nonpositive values. Retain valid positive prices. Four offline regression methods cover missing column, missing cell, nonpositive values, and valid prices.

## Evidence
Code and tests published, **NOT EXECUTED**. R257 pinned snapshot predates R262 and cannot validate this change. A fresh pinned run is required. PR draft/unmerged; no production/real orders. FASE_B=0/16; HP19=0/19; COST=R$0.
