# ET665.R40 — Drive-ID recovery and integration gate

Source originals: research/historical_sources/et665_r39/PROVENANCE.json (five original Google Drive IDs and SHA-256 hashes).

## Static findings
- P2131–2150: declares multiple PASS without running behavioral tests; modifies environment to match locks before checking drift; resulting certification is not trustworthy.
- P2405C: Windows absolute paths; import-time IO and output mutation; ranks on the same historical series; no independent OOS proof; hard-coded runtime stub. DO NOT IMPORT.
- P2357: missing chronology and fold independence; zero train PF previously yielded zero degradation.
- P2358: float NaN/infinity and absent provenance not adequately rejected; output 'PROMOTE' is not authorization.
- P2359: unknown FX symbols silently map to zero risk; lot-count proxy is not true correlation/notional exposure.

## Changes
- mind_trader/research/et665_r40_guarded_research.py: pure offline guards, strict chronology, finite metrics, explicit symbol/side validation, no promotion path.
- tests/test_et665_r40_guarded_research.py: 14 targeted unit tests (prepared, not yet executed in isolated Docker).

## Mandatory certification gate
1. Run `python -m unittest -v tests.test_et665_r40_guarded_research` inside Python 3.11 Docker, `--network none`, `--read-only`, nonprivileged.
2. Run existing M8/M9 financial-gateway regressions.
3. Confirm no imports from research archive into broker/gateway.
4. Verify independent source hashes against Drive originals.
5. For P2405C, require P2403E/P2404/P2405B independent datasets, OOS and Monte Carlo; no certification from in-sample PF.
6. For P2131, replace declared PASS with actual scenario executions and immutable evidence.

## Current certification
R39 original source archival: VERIFIED.
R40 implementation: PUBLISHED; behavioral certification: PENDING.
FTMO operational: NOT_CERTIFIED.
REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; PAPER_ONLY; no production changes.
