# ET665 — P2403E/P2404/P2405/P2406 causal revalidation
Date: 2026-11-09
Status: IMPLEMENTATION PATCHED / CERTIFICATION BLOCKED
Mode: PAPER_ONLY
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN

## Source recovery and integrity
- Canonical repository source: `mind_trader/data/raw/mt5/MT5_GER40_M15_raw.csv`
- GitHub blob SHA: `3640e32acd5f7259dda264e86ebfd9318f609b75`
- 5,000 rows; first timestamp `2026-03-27 10:30:00`; last timestamp `2026-06-19 21:45:00`.
- All 5,000 rows passed OHLC ordering checks in a direct content scan.
- Historical spread values (MT5 points): 50 (2,225 bars), 70 (1,058), 80 (972), 200 (253), 400 (492).
- A separate Drive file `GER40_CASH_M15_RAW.csv` has 75,000 rows from 2022-06-17 through 2026-07-07, but it has a large data gap: after 2025-12-30, the next observations are only on 2026-07-07. It is not a continuous extension of the 5,000-row 2026-03–06 series and must not be silently concatenated.

## Contract and execution-cost evidence
- MT5 symbol discovery for `DE40` on `MetaQuotes-Demo`: point=0.01, contract_size=1, volume_min=0.1, volume_step=0.1, volume_max=250, profit currency EUR, snapshot spread=50 points.
- This discovery snapshot is MetaQuotes-Demo, not proof of the FTMO server's exact trading conditions.
- FTMO's published information states index CFDs are commission-free: https://ftmo.com/en/blog/zero-commissions-on-indices/
- FTMO's 2026-07-28 trading update describes a 0.7% currency-conversion adjustment when profit currency differs from account currency, including GER40.cash (EUR profit currency) in a USD account: https://ftmo.com/en/blog/trading-updates/trading-update-28-jul-2026/
- The 5,000-row series ends 2026-06-19, before the 2026-07-28 conversion update. Do not apply the later adjustment retrospectively.
- The raw bars include variable spread. The patch converts spread points using explicit `point_size`. It requires an explicit FX conversion factor, commission schedule, financing schedule for overnight positions, and slippage assumption. Slippage is not measured by this OHLC dataset.
- The current adapter assumes BID-based MT5 OHLC. Confirm the exact price basis and FTMO server symbol specification before any broker-specific certification.

## Historical certification defects found
1. P2403E historical script did not generate strategy signals. It generated trade rows by deterministic hash-derived stride and holding period, then assigned returns from future close-to-close movement. This is synthetic replay, not execution of the candidate strategy rules.
2. P2404 computed correlations from those synthetic P2403E rows, aligning entry timestamps and filling absent timestamps with zero. The resulting historical certificate is not evidence of causal strategy-return correlation.
3. P2405E3 generated candidate combinations and novelty/priority scores. This is candidate enumeration, not performance validation.
4. P2405F historical script generated PF, win rate, expectancy, drawdown, sample size and passed-window counts from deterministic hash-based pseudo-random values. Its historical certification is invalid as behavioral performance evidence.
5. P2406's original runtime vote did not inspect context fields or direction and did not enforce the policy's family concentration cap. Its old test explicitly expected an empty context to approve a paper signal. The prior P2406 certificate is not valid for contextual voting.

## Integrated patch
- P2403E: strict OHLC validation; actual strategy signals required as input; next-bar entry; spread, slippage, commission, financing and conversion adjustment separated; no hash-based trade generation.
- P2404: synchronized daily realized returns, explicit calendar, minimum observation gate and pairwise Pearson matrix.
- P2405F: event-driven portfolio replay; fixed lot size per position; volume min/max/step; simultaneous entries share remaining aggregate risk capacity; chronological train/test with purge/embargo.
- P2405E3: explicitly classified as candidate generation only; cannot certify performance or promote candidates.
- P2406: session/regime/timeframe filtering, directional weighted confidence, unique edge quorum and family concentration cap.
- All runtime-promotion and real-execution paths remain disabled.

## Test evidence
- Local isolated suite: 11/11 PASS.
- GitHub suite added at `tests/test_et665_integrated_pipeline.py`, including validation of the canonical 5,000-row OHLC file. GitHub Actions result remains pending.
- Tests validate utility contracts and safety gates. They do not prove that the original P2402/P2405E3 candidate strategies generate valid signals or that broker costs/slippage are calibrated.

## Remaining blockers
1. Recover or implement explicit strategy signal rules for each candidate pattern; the old P2403E hash-stride replay is rejected.
2. Confirm exact FTMO MT5 server, account currency, symbol contract specification, point/tick size and volume limits.
3. Obtain execution/quote evidence to calibrate slippage and validate historical spread semantics.
4. Recover/derive timestamp-matched EURUSD conversion series where account currency is USD and profit currency is EUR.
5. Run the new pipeline on actual strategy signals, then complete independent review and GitHub Actions.
6. Record the BLOCKED status in the Drive Master Ledger when write permission is restored. No certification approval is requested or claimed.

## Safety decision
`CERTIFICATION=BLOCKED | RUNTIME_PROMOTION=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN`
