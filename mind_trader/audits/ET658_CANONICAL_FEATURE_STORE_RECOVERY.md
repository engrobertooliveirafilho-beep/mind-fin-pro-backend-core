# ET-658 — Canonical Feature Store manifest recovered and hash-verified (2026-11-05)
Source of truth: authenticated Google Drive historical tree `S21_R13_R2C/20260807_192356/manifest` (folder ID `1OPwmSIs_wolH_KU_PlwKfaMh9irfItGC`).
## Verified original files
- `TRADER_CANONICAL_FEATURE_STORE_MANIFEST_V1.csv` Drive ID `1kFeaGMr1f6mQ2NZ4_DEmL7ckk5RRNro3`; local raw SHA-256 `7b8d72ae3ee35876cebfd46f16176a85d60a82e04921f13c613696aec172e862`; matches historical R2C final report.
- `TRADER_CANONICAL_FEATURE_STORE_MANIFEST_V1.json` Drive ID `1pmlzRZ_wNHKLucTDQbsWhNP9zoQshLXZ`; SHA-256 `be48448c9848d1980c972b502f7dda7e6434bb5483aac7beec831912d6a8b9cc`; matches report.
- `TRADER_CANONICAL_FEATURE_STORE_MANIFEST_CONTRACT_V1.json` Drive ID `1HISYz59gSJ2THSXmwdeFbFd-a00-lzQw`; SHA-256 `a0969aa6d8e08a23cc5edba62e65b2541aa63f5ee3dc171e2b254651a60f94eb`; matches report.
## Validated content
CSV 58 rows, 58 unique symbols, all `M1`, required contract columns present. JSON 58 records. Contract declares `ACTIVE_MANIFEST_AUTHORITY_CONTRACT`, forbids heuristic symbol assignment, bulk data copy, S20 mutation, realized-outcome build, and decision-symbol map build without lineage proof. Some source SHA/rows fields explicitly `<UNAVAILABLE_IN_R12>`; **do not treat these as validated market dataset hashes**.
## Decision lineage and outcomes
R2C final report (Drive `1zIJMMJfiixzhp08Mfo11x_TOcL2f0z7g`): S20 84,000 decisions; `S20_DECISION_SYMBOL_COLUMN=<NULL>`; decision symbol authority FALSE. R2D final report (Drive `1ZeSiEvNIvDU8kKibLAVDkaxJHmBSmT2e`): 3 symbol-bearing manifests but 0 explicit key mappings, 0/84,000 decision join coverage; outcome ledger NOT BUILT. R6-R5-R1 final report (Drive `1sxlUpBmot8xH2zeQB3omWGxZw8_NmWWI`): 3 writer-class definitions, 0 resolved writer modules, canonical writer unresolved.
## Integration gate
Original manifest **certified for historical file integrity and schema only**. No symbol-decision-outcome join fabricated; no new motor; no live integration; `S21_CERTIFIED=FALSE`, `READY_FOR_S22=FALSE`, `FTMO_BLOCKED`, `REAL_ORDERS=0`. Next recover explicit writer-instance lineage and decision-key provenance before joining.
