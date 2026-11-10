# ET665.R258 — DE40 canonical OHLC location and chronological gate
Date 2026-11-10 | PAPER_ONLY | NO EXECUTION AUTHORITY

New original Drive evidence:
- P2403D2 audit Drive 1lk5tZReRoeMMk_NA5CTTuABAZOG61vzt: selected mind_trader/data/raw/mt5/MT5_GER40_M15_raw.csv (GER40 M15), among 430 canonical OHLC, 180 DE40 candidates.
- P2403E audit Drive 12IpbH95cdfLVI9qRvDqUuevx_62uUgul: 5000 candles parsed, 4400 replay trade rows, 20 edge series; invalidated de40_cycle_events.csv as source. This is historical audit, NOT evidence original OHLC bytes were recovered now.
- P2383C audit Drive 1NIO6cIwp4hAGLjwhxDVhsmHZYA4qeVIx: chronological 80/20 last 20% OOS, 0 samples, 0 promoted, 7 rejected; explicitly NOT_CERTIFIED_ORIGINAL_EDGE and missing exact P2378/P2379 entry logic. No actual train/test timestamps disclosed.
- File-list manifests: C_USERS_MINDFIN_TRADER_FILES_FROM_RAW.txt Drive 1ENfKRxN8jNeb3vHz7gm99Wh6zcynCXaj names Desktop/mind-fin-pro-backend-core/mind_trader/data/raw/mt5/MT5_GER40_M15_raw.csv. D_DRIVE_TRADER_FILES_FROM_RAW.txt Drive 12GvANYwlVRVWZ5Wv6UNMxmQ1JzffdsG3 names MIND_TEMP/.../RELEASE_BOUNDARY/CHANGED_FILES/mind_trader/data/raw/mt5/MT5_GER40_M15_raw.csv and historical FTMO_PROFILE/MQL5/Files/mind_ger40_5y_p2363b_DE40_M15_csv. These are PATH MANIFESTS, not verified current downloadable source files. Never connect to FTMO or a terminal.

Scoped Drive exact filename searches for MT5_GER40_M15_raw.csv, de40_patched_replay_candidates.csv, de40_replay_after_patch_all.csv yielded zero actual CSV file results. Historical P2381/P2382 evidence folders contain only run and pytest logs. No original executor or timestamped trade rows recovered; no independent walk-forward run possible. Fail closed; do not fabricate data, split dates, trades or performance.

Next steps: identify original binary/blob location from archived Drive inventory, verify SHA256/row count/timestamps and timezone; recover P2378/79/81/82 code and CSVs; align row IDs to canonical OHLC, validate pre-signal-only features, embargo/purge split, replay with fees and intrabar adversarial paths, compare P2383C failure and P2382 anomalous PF=999.

Ledger V1 ET-708 pending Google Docs permission (prior 403); this GitHub audit is not a Doc update.
MAIN untouched | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST R$0 | CERTIFICATION BLOCKED.
