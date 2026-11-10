# ET665 — P2405/P2406 causal revalidation
Date: 2026-11-09
Status: BLOCKED / PAPER_ONLY

- 3,960 event rows from 18 P2404 candidate edges were replayed; 2 additional historical edges exist outside the P2404 pool.
- Three chronological out-of-sample folds with 165-minute embargo produced PF 0.7548 / 1.4109 / 0.8436 and net expectancy -0.1652R / +0.1806R / -0.1038R using illustrative total costs of 0.05R/trade.
- Event-driven accounting fixes cash risk at entry and caps aggregate open risk at 2%; simultaneous entries are prorated to available risk.
- Cost sensitivity (illustrative assumptions only): 0.05R total cost PF 1.069, 0.10R PF 0.975, 0.20R PF 0.817 on the selected candidate universe.
- Actual broker costs are not available; the original GER40 M15 OHLC file referenced by the historical replay was not recovered.
- P2406 now has a separate contextual voter prototype with market-context matching, quorum and family concentration enforcement; runtime remains disabled.
- This is a research harness, not a certified trading engine. No production integration, no real orders, no FTMO real.

The historical P2405/P2405B/P2405H/P2406 certification labels must be treated as invalid for behavioral certification until the raw OHLC, contract specifications and complete causal walk-forward gates pass.
