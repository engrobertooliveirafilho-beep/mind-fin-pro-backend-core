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
- The raw bars include variable spread. The patch converts spread points using explicit `point_size`. It requires explicit commission, financing and slippage inputs; slippage is not measured by OHLC and has no zero-cost default.
- Canonical EURUSD M15 file: `mind_trader/data/raw/mt5/MT5_EURUSD_M15_raw.csv`; 5,000 rows; 2026-04-08 22:00 through 2026-06-19 23:45; GitHub blob SHA `9bde7a21aeabd514d871eb8d5c739231cd853b4e`.
- P2403E now accepts the original MT5 `time` column and can use the last completed EURUSD M15 candle at or before the trade exit. The EURUSD series begins 2026-04-08, so it does not cover the first part of the GER40 sample (2026-03-27 through 2026-04-08); USD-account conversion for that interval remains blocked unless another causal FX source is recovered.
- The adapter requires an explicit currency-conversion adjustment when account and profit currencies differ; it does not apply the post-2026-07-28 FTMO adjustment retrospectively.
- The current adapter assumes BID-based MT5 OHLC. Confirm the exact price basis and FTMO server symbol specification before any broker-specific certification.

## Historical certification defects found
1. P2403E historical script did not generate strategy signals. It generated trade rows by deterministic hash-derived stride and holding period, then assigned returns from future close-to-close movement. This is synthetic replay, not execution of the candidate strategy rules.
2. P2404 computed correlations from those synthetic P2403E rows, aligning entry timestamps and filling absent timestamps with zero. The resulting historical certificate is not evidence of causal strategy-return correlation.
3. P2405E3 generated candidate combinations and novelty/priority scores. This is candidate enumeration, not performance validation.
4. P2405F historical script generated PF, win rate, expectancy, drawdown, sample size and passed-window counts from deterministic hash-based pseudo-random values. Its historical certification is invalid as behavioral performance evidence.
5. P2406's original runtime vote did not inspect context fields or direction and did not enforce the policy's family concentration cap. Its old test explicitly expected an empty context to approve a paper signal. The prior P2406 certificate is not valid for contextual voting.

## Integrated patch
- P2403E: strict OHLC validation; actual strategy signals required as input; next-bar entry; spread, slippage, commission, financing and conversion adjustment separated; stop-risk sizing includes entry spread/slippage and requires an explicit stop-side spread assumption for SELL trades; no hash-based trade generation.
- P2404: synchronized daily realized returns, explicit calendar, minimum observation gate and pairwise Pearson matrix.
- P2405F: event-driven portfolio replay; fixed lot size per position; volume min/max/step; simultaneous entries share remaining aggregate risk capacity; chronological train/test with purge/embargo.
- P2405E3: explicitly classified as candidate generation only; cannot certify performance or promote candidates.
- P2406: session/regime/timeframe filtering, directional weighted confidence, unique edge quorum and family concentration cap.
- Actual P2406 roster audit: 9 members occupy 9 unique session/regime/timeframe combinations, so the maximum context-matched vote count is 1 against quorum=3. The global family weight maximum is 34.066%, below 40%; however, within each isolated context the only active family's concentration is 100%. The current roster cannot satisfy contextual quorum and family concentration simultaneously.
- All runtime-promotion and real-execution paths remain disabled.

## Test evidence
- Local isolated suite: 15/15 PASS.
- GitHub suite added at `tests/test_et665_integrated_pipeline.py` (17 tests), including canonical GER40 and EURUSD source checks, causal FX no-lookahead, stop-side spread sizing and the actual nine-member P2406 roster. GitHub Actions result remains pending.
- Tests validate utility contracts and safety gates. They do not prove that the original P2402/P2405E3 candidate strategies generate valid signals or that broker costs/slippage are calibrated.

## Remaining blockers
1. Recover or implement explicit strategy signal rules for each candidate pattern; the old P2403E hash-stride replay is rejected.
2. Confirm exact FTMO MT5 server, account currency, symbol contract specification, point/tick size and volume limits.
3. Obtain execution/quote evidence to calibrate slippage and validate historical spread semantics.
4. Recover/derive EURUSD coverage for 2026-03-27 through 2026-04-08 where account currency is USD and profit currency is EUR; use the recovered M15 series causally for the remaining overlap.
5. Run the new pipeline on actual strategy signals, then complete independent review and GitHub Actions.
6. Record the BLOCKED status in the Drive Master Ledger when write permission is restored. No certification approval is requested or claimed.

## Safety decision
`CERTIFICATION=BLOCKED | RUNTIME_PROMOTION=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN`
