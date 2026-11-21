# Trader.1.001 exporter recovery and static audit — 2026-11-21

## Drive source of truth
Original MQ5: `gdrive:MIND/__CORE_CANON/trader/exporters/TRADER_1_001_R2_R1_R2/20260716_215809/source/TRADER_1_001_FTMO_M1_SATURATION_EXPORT.mq5`
Original MQ5 size: 12,262 bytes.
Original MQ5 SHA-256 independently recalculated from the recovered raw attachment: `ee4fa0a7fdd127d04b736f0a963198192f531fc4eaf0056deea51ae1812d1e5f`.
Compiled EX5 SHA-256 from the historical certificate: `7defb52581d2b13085c3b42813c5484e7c095d8ccba76e8c5b99c9a0043375ba`.

## Historical evidence reconciled
- R2-R1 certificate: SymbolExist signature repaired; 58 assets; M1; compile log says 0 errors and 0 warnings; EX5 exists.
- R2-R1-R2: inventory stabilized after excluding the active transcript from its own hash; local certificate status `LOCAL_CERTIFIED`.
- R2-R1-R3: corrected remote relative-path layout. Final rclone check on 2026-07-16 22:03:39 reports **0 differences, 13 matching files**.
- The R3 certificate itself says `READY_FOR_FINAL_DRIVE_VERIFICATION`; the later final-check log supplies the successful remote comparison.
- Historical source is preserved unchanged as an archival copy. Git copy is for review; Drive remains byte-level authority.

## Important status correction
The 58-symbol M1 exporter was compiled and its artifacts/evidence were synchronized to Drive. **There is no evidence in this chain that the exporter was actually run to collect the 58 histories.** Its certificate explicitly says the next step is execution on an authenticated FTMO terminal.

## Static source findings
- Read-only source: uses MT5 `CopyRates` and CSV file operations; no order-submission API was found.
- Original completion marker writes `STATUS=COMPLETE` unconditionally, even when fewer than 58 assets were exported or manifest rename failed.
- Original per-symbol status `SATURATED` is ambiguous when fewer than the configured 1,000,000 bars were returned.
- These two reporting defects are corrected in a separate candidate V2 source. Original MQ5/EX5 and historical certificates are not modified.
- V2 is **not compiled** in this environment. It must pass MetaEditor compilation before terminal use.

## Candidate V2 change
- `EXPORT_RUN_COMPLETE` only when all 58 assets exported, none unavailable, and the final manifest was renamed.
- Otherwise the marker reports `EXPORT_RUN_INCOMPLETE`.
- `STABLE_AVAILABLE_HISTORY` replaces the ambiguous `SATURATED` status when fewer than the configured maximum bars are returned.
- Historical compile evidence does not certify candidate V2.

## Next controlled gate
Compile candidate V2 in MetaEditor on the authenticated terminal; verify 0 errors/0 warnings and EX5 SHA; only then run the read-only M1 export. Validate all 58 CSVs, manifest, timestamps, OHLC integrity, per-symbol coverage and Drive hashes before declaring dataset certified.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | PRODUCTION=INTACTA | EXPORT_EXECUTED=FALSE | V2_COMPILED=FALSE | COST=R$0`
