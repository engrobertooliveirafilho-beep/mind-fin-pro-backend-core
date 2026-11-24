# P2383D — forensic reconciliation of original outputs
Date: 2026-11-24
Repository: engrobertooliveirafilho-beep/mind-fin-pro-backend-core
Branch: audit/p2376-p2383d-causal-reconciliation-20261123

## Scope
Read-only reconstruction of the original P2383D Drive outputs. No source code was changed and no strategy was promoted.

## Source artifacts and SHA-256
- Drive folder: 1ZuNFZoqaLm9G9_de4E0GEWwruLyTPa7M
- AUDIT_FINAL.txt: 1Hx2hxuWjzPJ0WuZCRm9oU-LzeRV5cxRd
- summary.json: 1HIy5y6czqvfD4XWPxngxsTOJEzjN7AYr — SHA256 94156b64f7412e8e3fc74632a7aee4bd28492059a4088eaaaea082c846117c77
- playbook source: 1_oAlnKpAS1Htm9FgqnBroOrLeqogBcQu — SHA256 1e04fb80bdc98b5a7235b8f25a4b80d729a5df841e9a84a5ab686dcd40fa4efb
- OOS events: 1sBZIoBZTomr_-Bu5UpJdLgjxURY16KdX — SHA256 4c57450877c4bfe407d57e9979158714f4a5de5de3e383561d77a0898f185a67
- matched trades: 1FtHS_xASRVJmHbifpwcNBcib6PWuor5a — SHA256 91e4447d04352412a3561dfb1dce123dce6b218e337afc34900e49e2ec85c010
- timeframe audit: 1yn2A_w2L2gjBBJfldaolsFwCMsaxTSn4

## Reproduced structural findings
1. OOS events file contains 77,871 rows across M1/M5/M15/M30/H1/H4/D1.
2. Matched-trades file contains 3,980 rows but only 796 unique event identities (entry_time, symbol, timeframe, direction).
3. Every one of the 796 identities appears exactly five times, once for each of five family labels. All five rows per identity have the same realized_r. Thus the 3,980 rows are not 3,980 independent trades; they represent 796 unique event outcomes repeated across five family labels.
4. The report's PF 1.033224, expectancy 0.009917R and win rate 46.859296% remain numerically unchanged after deduplicating exact repeated event identities. Sample count changes from 3,980 to 796.
5. Reported max drawdown 111.593895R is five times the drawdown obtained after deduplicating the repeated event outcomes in chronological order: 30.906699R. The original summary's drawdown is therefore affected by repeated counting.
6. Only M1 (1,170), M5 (1,425) and M15 (1,385) have matched trades. M30, H1, H4 and D1 have zero matched trades, despite OOS events existing for those timeframes.
7. P2383D summary explicitly says it matches contextual keys (timeframe + regime + session + footprint + lifecycle), not exact price-entry rules or tick-level orders. Therefore its phrase “exact playbook to raw candle” must not be interpreted as exact trade reconstruction.
8. The historical output labels five playbooks promoted, but global PF is 1.033224, expectancy 0.009917R and the per-timeframe audit marks every timeframe passed=false. Historical promotion is not independent certification.

## Decision
P2383D is NOT certified for strategy promotion or live/PAPER operation. Keep all five historical promotions quarantined as research candidates. Require original executable validator source, original tests, exact playbook-to-event linkage, de-duplication by event identity, complete timeframe reconciliation, independent chronological walk-forward, realistic costs and a fresh readback before any promotion.

## Safety
PAPER_ONLY. REAL_ORDERS=FORBIDDEN. FTMO_REAL=FORBIDDEN. No tests were re-run here; this is a data/output forensic audit only.
