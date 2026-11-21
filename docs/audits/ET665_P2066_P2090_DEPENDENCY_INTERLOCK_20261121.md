# ET665 — Evidence reconciliation P2066–P2090, 2026-11-21

## Drive primary evidence (read directly)
- Original P2066–P2070 readiness JSON: Drive file 1ehwUddbLPDcsERWuH5o7PNJJ3_QFMvD7, timestamp 2026-06-18. Historical 3-specialist portfolio, P2067 fixed paper micro-size 0.01, daily loss 1%, total drawdown 3%.
- P2071–P2080 audit: Drive file 1fo3wvD_8WjmPlLi6GAHr60V3LIhD-34_. Historical status FAIL, P2080 PENDING, 1500 cycles, 4329 signals, 411 closed trades, P&L -969.3669; historical drawdown_abs reported 0.0 and is not credible as maximum drawdown.
- P2081–P2090 audit: Drive file 1oWQwpzBIYmuDjJc6pK1KOPu84fPFXQX5. Historical status PASS, claimed governance certification, but explicitly consumes P2071–P2080 certification file as dependency. Its metrics report mark-to-market P&L -953.05314 and drawdown -0.00953053. Historical P2081–P2090 PASS **cannot override** the upstream P2080 FAIL/PENDING.
- Search hits for strategy names and agents were mostly console/evidence/inventory references, not authenticated original strategy adapter source. Do not count those as recovered motors or agents.

## Branch technical changes
- Paper quantity capped at 0.01 (synthetic unit, not broker lot certification).
- Realized/unrealized P&L quantity-weighted.
- Invalid signal side and nonfinite prices/confidence rejected.
- Daily realized loss gate 1%, total loss gate 3%, one position per specialist, max three positions.
- Admission now uses marked-to-market equity for unrealized losses.
- Boundary RSI tests and peak-to-trough drawdown correction.
- Regression tests committed but not yet run on the complete GitHub branch.

## Remaining critical defects / gates
- Current risk admission is a simplified check, not a certified P2067 risk engine. Full intraday high-water marks, persistent sessions, mark-to-market breach response, spread, slippage, commission, fill mechanics, symbol/contract sizing, and execution cost attribution remain unverified.
- Original MEAN_REVERSION and TREND_PULLBACK strategy adapters not recovered; fail closed.
- P2081–P2090 governance cannot be certified while P2080 and its real-time feed remain uncertified.
- Current data feed synthetic only. No broker or real-order execution.
- Container cannot resolve github.com, so branch code has not been run in local Docker or pytest; do not report test PASS.

## Status
GITHUB_BRANCH_PATCHED=TRUE
GITHUB_READBACK=TRUE
TESTS_PUBLISHED=TRUE
TESTS_EXECUTED=FALSE
P2067_RISK_CERTIFIED=FALSE
P2080_E2E_CERTIFIED=FALSE
P2090_GOVERNANCE_CERTIFIED=FALSE
PAPER_ONLY=TRUE
REAL_ORDERS=FORBIDDEN
COST_BRL=0

## Chronological correction — P2071–P2080B discovered on Drive
- New source recovered: Drive console_output_P2071_2080B.txt, ID 1KYxzOPfi2VjwZs2TwIMQThapJ_fL278n; matching updated P2071_2080_AUDIT.md ID 18YH2y48oGqICHluabKydr318hvxAXMst.
- Both explicitly identify patch P2071_2080B_CERTIFICATION_DRAWDOWN_REPAIR and historical PASS for P2071–P2080, superseding the earlier FAIL/PENDING audit for that *historical version*.
- 1500 synthetic cycles; 4329 signals; 411 closed trades; 3 open; initial equity 100000; final realized 99030.6331; marked equity 99046.94686; current drawdown -953.05314; trough 99026.36134. These are historical simulation metrics, not current certified broker execution.
- Therefore the earlier statement that **all** P2081 historical PASS claims contradict P2080 must be narrowed: the P2080B historical PASS exists. Provenance/ordering of the exact consumed JSON and behavioral replay remain unverified; the present patched branch deliberately leaves P2074 risk/fill validation PENDING.
- Additional current branch fix: P2074 now rejects cross-symbol marks and invalid mid/spread before changing risk state; 12 parametrized regression cases published, not yet executed.
- HISTORICAL_P2080B_PASS=DOCUMENTED; CURRENT_P2080_E2E_CERTIFIED=FALSE; P2090_CURRENT_CERTIFIED=FALSE.

## P2078 integrated PAPER restoration — 2026-11-21
- Runtime now persists `executor_snapshot` and restores it with `PaperPortfolioExecutor.restore_state`, checking complete round-trip equality and marked equity.
- Code commit `7945a4410a0659435e98bfae3ce770c350ae51da`; test commit `0b1a4c794251a8cb1b5d02db330d3843302f332e`.
- `P2079` persistence PASS is restricted to serialized readback equality; `P2078` remains PENDING because no independent interrupted-process replay was executed.
- Current branch regression execution: BLOCKED (no local GitHub checkout through DNS; no verified workflow); E2E_CERTIFIED=FALSE.

## Drive reconciliation — P2151+ readiness dossier (2026-11-21 discovery)
- Original Drive document: P2151_PLUS_READINESS_DOSSIER.md, file ID 1nQcgBkC1wRe9rlphS574m_A0e0W0Ms6e (read directly).
- It asserts historical PASS for seven blocks: P2071_2080, P2081_2090, P2091_2100, P2101_2110, P2111_2120, P2121_PLUS, P2131_2150. Each points to a distinct data/runtime/*/evidence/*_FINAL_CERTIFICATION.json.
- This is **documentary evidence of prior assertions only**; those seven underlying certification JSON artifacts, exact source hashes, current integration and full regression runs were NOT retrieved or independently verified in this mission.
- Historical deployment decision: APPROVED_FOR_PAPER_ONLY_SIMULATION_REVIEW; real orders, broker connections, MT5 order sending and financial execution forbidden.
- Reconciliation: HISTORICAL_P2151_READINESS_ASSERTED=TRUE; UNDERLYING_CERTIFICATION_JSON_VERIFIED=FALSE; CURRENT_E2E_CERTIFIED=FALSE.
- Follow-up is to locate and inspect the exact seven certification JSON artifacts and their original source/dependency hashes, then run offline tests. Do not promote historical PASS to current certification.

## Drive original evidence recovery — P2062 and P2151 (2026-11-21)
- Drive cat_evidence_0000168.stdout.txt ID 1Sw-ag7j4aEZDFXzb4Vzod_lAttCIhkVx: recovered machine-readable historical P2062_REAL_LOGIC_BACKTEST_ENGINE output, status PASS, RESEARCH_ONLY, 5 specialists, 50,000 rows, 3 validated / 2 failed, with detailed sampled trades for XAUUSD_M1_REALDNA_0004. This is more granular than the previously recovered dossier; source code and raw OHLC CSV remain unverified.
- Drive cat_evidence_0000206.stdout.txt ID 1C7Dz3GqJERFT3_VATxRqLtCcWLl63ML1: recovered historical P2151+ program completion output, including exact output paths for final JSON, gate review, ZIP package and dossier. It is an execution output record, not independently retrieved underlying certification JSON.
- The Drive console_output_P2151_PLUS.txt ID 1O5DWAb54UL-EzWSd2jr8xhiVrqUdHf1A contains seven reported certification hashes. These are unverified declarations until actual certification files are recovered and hashed.
- RECOVERED_P2062_MACHINE_OUTPUT=TRUE; RECOVERED_P2151_OUTPUT_PATHS=TRUE; ORIGINAL_P2062_CODE_VERIFIED=FALSE; ORIGINAL_P2151_FINAL_JSON_VERIFIED=FALSE; CURRENT_E2E_CERTIFIED=FALSE.

## P2061B → P2062 specialist-level historical reconciliation (Drive machine outputs)
- P2061B original stdout: cat_evidence_0000167.stdout.txt (Drive 1yoMkOATDHTyw5h3RME9hCysoTOt025z2), generated 2026-06-18T08:37:34Z. Factory generated five DNA logic types: TREND_PULLBACK, MOMENTUM, MEAN_REVERSION, RANGE_REVERSION, VOLATILITY_BREAKOUT. Declared output data/specialists/P2061B/REAL_LOGIC_SPECIALISTS.json (original JSON not yet recovered).
- P2062 original stdout: cat_evidence_0000168.stdout.txt (Drive 1Sw-ag7j4aEZDFXzb4Vzod_lAttCIhkVx). Historical 50,000-row research-only backtest.
- VALIDATED: XAUUSD_M1_REALDNA_0004 RANGE_REVERSION (15,847 trades; PnL +1269.77); XAUUSD_M1_REALDNA_0003 MEAN_REVERSION (5,742; +541.53); XAUUSD_M1_REALDNA_0001 TREND_PULLBACK (7,132; +356.07).
- REJECTED: XAUUSD_M1_REALDNA_0005 VOLATILITY_BREAKOUT (19,842; -1023.18); XAUUSD_M1_REALDNA_0002 MOMENTUM (25,157; -1247.68).
- Reconciled validated aggregate PnL = +2167.37 (1269.77+541.53+356.07), matching prior P2066–P2070 historical dossier; rejected strategies MUST NOT be silently promoted.
- These are recovered historical results, not independently replayed tests. GitHub default-branch search for exact P2062 engine identifier returned no matching file; does not prove absence in other branches or Drive.
- P2061B_FACTORY_OUTPUT_RECOVERED=TRUE; P2062_FIVE_SPECIALIST_RESULTS_RECOVERED=TRUE; ORIGINAL_DNA_JSON_RECOVERED=FALSE; P2062_ENGINE_SOURCE_RECOVERED=FALSE; P2062_REPLAY_CERTIFIED=FALSE.

## Newly recovered chronological P2063G → P2064 original machine outputs
- P2063G original stdout Drive ID 14amX7y7kAxGBaIRTnUMT0_t34kl9JnnE: historical FINAL_REAL_LOGIC_CERTIFICATION PASS, three final locked specialists, output data/specialists/P2063/REAL_LOGIC_FINAL_LOCKED_SPECIALISTS.json. Ranks: REALDNA_0004 RANGE_REVERSION score 325, REALDNA_0003 MEAN_REVERSION score 291, REALDNA_0001 TREND_PULLBACK score 280. Five historical gates marked true for each: walk_forward, monte_carlo, spread, slippage, regime.
- P2064 original stdout Drive ID 10FjXI5QTv83jJwVm1iUGW5RZEN_RvjeA: historical REAL_MARKET_PAPER_RUNTIME PASS on source data/features/P2060/XAUUSD_M1_50000_FEATURES_200_WITH_OHLC.csv, 3 passed, 0 failed, 50,000 rows. Top REALDNA_0004 15,847 paper trades, final equity 101269.77 from 100000, total PnL 1269.77. The output includes event samples.
- These are historical outputs; original P2063 JSON and P2064 OHLC feature CSV not yet fetched/hashed/replayed. Current P2073 runtime only implements RANGE_REVERSION; MEAN_REVERSION and TREND_PULLBACK adapters remain missing. Do not treat the P2063G historical five gates as current test execution.
- P2063G_OUTPUT_RECOVERED=TRUE; P2064_OUTPUT_RECOVERED=TRUE; ORIGINAL_P2064_OHLC_RECOVERED=FALSE; CURRENT_THREE_ENGINE_E2E_CERTIFIED=FALSE.
